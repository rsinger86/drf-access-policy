import importlib
from dataclasses import asdict, dataclass, field
from typing import List, Union

from django.conf import settings
from django.db.models import prefetch_related_objects
from pyparsing import infixNotation, opAssoc
from rest_framework import permissions

from rest_access_policy import AccessPolicyException

from .parsing import BoolAnd, BoolNot, BoolOperand, BoolOr, ConditionOperand


class AnonymousUser(object):
    def __init__(self):
        self.pk = None
        self.is_anonymous = True
        self.is_staff = False
        self.is_superuser = False


class AccessEnforcement(object):
    _action: str
    _allowed: bool

    def __init__(self, action: str, allowed: bool):
        self._action = action
        self._allowed = allowed

    @property
    def action(self) -> str:
        return self._action

    @property
    def allowed(self) -> bool:
        return self._allowed


@dataclass
class Statement:
    principal: Union[List[str], str]
    action: Union[List[str], str]
    effect: str = "deny"  # allow, deny
    condition: Union[List[str], str] = field(default_factory=list)
    condition_expression: Union[List[str], str] = field(default_factory=list)

    def __post_init__(self):
        permitted = ("allow", "deny")

        if self.effect not in ("allow", "deny"):
            raise Exception(f"effect must be one of {permitted}")


class AccessPolicy(permissions.BasePermission):
    statements: List[Union[dict, Statement]] = []
    field_permissions: dict = {}
    id = None
    group_prefix = "group:"
    id_prefix = "id:"

    def has_permission(self, request, view) -> bool:
        action = self._get_invoked_action(view)
        statements = self.get_policy_statements(request, view)

        if len(statements) == 0:
            return False

        allowed = self._evaluate_statements(statements, request, view, action)
        request.access_enforcement = AccessEnforcement(action=action, allowed=allowed)
        return allowed

    def get_policy_statements(self, request, view) -> List[Union[dict, Statement]]:
        return self.statements

    def get_user_group_values(self, user) -> List[str]:
        if user.is_anonymous:
            return []

        prefetch_related_objects([user], "groups")
        return [g.name for g in user.groups.all()]

    @classmethod
    def scope_queryset(cls, request, qs):
        return qs.none()

    @classmethod
    def scope_fields(cls, request, fields: dict, instance=None) -> dict:
        return fields

    def _get_invoked_action(self, view) -> str:
        """
        If a CBV, the name of the method. If a regular function view,
        the name of the function.
        """
        if hasattr(view, "action"):
            if hasattr(view, "action_map"):
                return view.action or list(view.action_map.values())[0]
            return view.action

        elif hasattr(view, "__class__"):
            return view.__class__.__name__

        raise AccessPolicyException("Could not determine action of request")

    def _evaluate_statements(
        self, statements: List[Union[dict, Statement]], request, view, action: str
    ) -> bool:
        statements = self._normalize_statements(statements)
        matched = self._get_statements_matching_principal(request, statements)
        matched = self._get_statements_matching_action(request, action, matched)

        matched = self._get_statements_matching_conditions(
            request, view, action=action, statements=matched, is_expression=False
        )

        matched = self._get_statements_matching_conditions(
            request, view, action=action, statements=matched, is_expression=True
        )

        denied = [_ for _ in matched if _["effect"] != "allow"]

        if len(matched) == 0 or len(denied) > 0:
            return False

        return True

    def _normalize_statements(
        self, statements: List[Union[dict, Statement]]
    ) -> List[dict]:
        normalized = []

        for statement in statements:
            if isinstance(statement, Statement):
                statement = asdict(statement)

            if isinstance(statement["principal"], str):
                statement["principal"] = [statement["principal"]]

            if isinstance(statement["action"], str):
                statement["action"] = [statement["action"]]

            if "condition" not in statement:
                statement["condition"] = []
            elif isinstance(statement["condition"], str):
                statement["condition"] = [statement["condition"]]

            if "condition_expression" not in statement:
                statement["condition_expression"] = []
            elif isinstance(statement["condition_expression"], str):
                statement["condition_expression"] = [statement["condition_expression"]]

            normalized.append(statement)

        return normalized

    @classmethod
    def _get_statements_matching_principal(
        cls, request, statements: List[dict]
    ) -> List[dict]:
        user = request.user or AnonymousUser()
        user_roles = None
        matched = []

        for statement in statements:
            principals = statement["principal"]
            found = False

            if "*" in principals:
                found = True
            elif "admin" in principals and user.is_superuser:
                found = True
            elif "staff" in principals and user.is_staff:
                found = True
            elif "authenticated" in principals and not user.is_anonymous:
                found = True
            elif "anonymous" in principals and user.is_anonymous:
                found = True
            elif cls.id_prefix + str(user.pk) in principals:
                found = True
            else:
                if not user_roles:
                    user_roles = cls().get_user_group_values(user)

                for user_role in user_roles:
                    if cls.group_prefix + user_role in principals:
                        found = True
                        break

            if found:
                matched.append(statement)

        return matched

    def _get_statements_matching_action(
        self, request, action: str, statements: List[dict]
    ):
        """
        Filter statements and return only those that match the specified
        action.
        """
        matched = []
        SAFE_METHODS = ("GET", "HEAD", "OPTIONS")
        http_method = f"<method:{request.method.lower()}>"

        for statement in statements:
            if action in statement["action"] or "*" in statement["action"]:
                matched.append(statement)
            elif http_method in statement["action"]:
                matched.append(statement)
            elif (
                "<safe_methods>" in statement["action"]
                and request.method in SAFE_METHODS
            ):
                matched.append(statement)

        return matched

    def _get_statements_matching_conditions(
        self, request, view, *, action: str, statements: List[dict], is_expression: bool
    ):
        """
        Filter statements and only return those that match all of their
        custom context conditions; if no conditions are provided then
        the statement should be returned.
        """
        matched = []
        element_key = "condition_expression" if is_expression else "condition"

        for statement in statements:
            conditions = statement[element_key]

            if len(conditions) == 0:
                matched.append(statement)
                continue

            fails = 0

            boolOperand = BoolOperand()

            for condition in conditions:
                if is_expression:
                    check_cond_fn = lambda cond: self._check_condition(
                        cond, request, view, action
                    )

                    boolOperand.setParseAction(
                        lambda token: ConditionOperand(token, check_cond_fn)
                    )

                    boolExpr = infixNotation(
                        boolOperand,
                        [
                            ("not", 1, opAssoc.RIGHT, BoolNot),
                            ("and", 2, opAssoc.LEFT, BoolAnd),
                            ("or", 2, opAssoc.LEFT, BoolOr),
                        ],
                    )

                    passed = bool(boolExpr.parseString(condition)[0])
                else:
                    passed = self._check_condition(condition, request, view, action)

                if not passed:
                    fails += 1
                    break

            if fails == 0:
                matched.append(statement)

        return matched

    def _check_condition(self, condition: str, request, view, action: str):
        """
        Evaluate a custom context condition; if method does not exist on
        the access policy class, then return False.
        Condition value can contain a value that is passed to method, if
        formatted as `<method_name>:<arg_value>`.
        """
        parts = condition.split(":", 1)
        method_name = parts[0]
        arg = parts[1] if len(parts) == 2 else None
        method = self._get_condition_method(method_name)

        if arg is not None:
            result = method(request, view, action, arg)
        else:
            result = method(request, view, action)

        if type(result) is not bool:
            raise AccessPolicyException(
                f"condition '{condition}' must return true/false, not {type(result)}"
            )

        return result

    def _get_condition_method(self, method_name: str):
        if hasattr(self, method_name):
            return getattr(self, method_name)

        if hasattr(settings, "DRF_ACCESS_POLICY"):
            module_paths = settings.DRF_ACCESS_POLICY.get("reusable_conditions")

            if module_paths:
                if not isinstance(module_paths, (str, list, tuple)):
                    raise ValueError(
                        "Define 'resusable_conditions' as list, tuple or str"
                    )

                module_paths = (
                    [module_paths] if isinstance(module_paths, str) else module_paths
                )

                for module_path in module_paths:
                    module = importlib.import_module(module_path)

                    if hasattr(module, method_name):
                        return getattr(module, method_name)

        raise AccessPolicyException(
            f"condition '{method_name}' must be a method on the access policy "
            f"or be defined in the 'reusable_conditions' module"
        )
