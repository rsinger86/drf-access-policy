import importlib
from typing import List, Optional, Union

from django.conf import settings
from django.db.models import prefetch_related_objects
from rest_framework import permissions

from rest_access_policy import AccessPolicyException

from .parsing import get_parser


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


class Statement(object):
    principal: List[str]
    action: List[str]
    condition: List[str]
    condition_expression: List[str]
    effect: str

    def __init__(
        self,
        *,
        principal: Union[str, List[str]],
        action: Union[str, List[str]],
        effect: str,
        condition: Optional[Union[str, List[str]]] = None,
        condition_expression: Optional[Union[str, List[str]]] = None,
    ) -> None:
        condition = condition or []
        condition_expression = condition_expression or []

        if isinstance(principal, str):
            principal = [principal]

        if isinstance(action, str):
            action = [action]

        if isinstance(condition, str):
            condition = [condition]

        if isinstance(condition_expression, str):
            condition_expression = [condition_expression]

        if effect not in ("allow", "deny"):
            raise AccessPolicyException(
                f"Must set 'effect' to 'allow' or 'deny', not: {effect}."
            )

        self.principal = principal
        self.action = action
        self.condition = condition
        self.effect = effect
        self.condition_expression = condition_expression

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "effect": self.effect,
            "principal": self.principal,
            "condition": self.condition,
            "condition_expression": self.condition_expression,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Statement":
        return cls(
            principal=data.get("principal"),
            effect=data.get("effect"),
            action=data.get("action"),
            condition=data.get("condition"),
            condition_expression=data.get("condition_expression"),
        )

    def __eq__(self, other: "Statement"):
        return self.to_dict() == other.to_dict()


class AccessPolicy(permissions.BasePermission):
    compiled_statements: Optional[List[Statement]] = None
    statements: List[dict] = []
    field_permissions: dict = {}
    id = None
    group_prefix = "group:"
    id_prefix = "id:"

    def __init_subclass__(cls) -> None:
        compiled_statements = []

        if cls.statements:
            for raw_statement in cls.statements:
                compiled_statements.append(
                    Statement(
                        principal=raw_statement.get("principal"),
                        action=raw_statement.get("action"),
                        effect=raw_statement.get("effect"),
                        condition=raw_statement.get("condition"),
                        condition_expression=raw_statement.get("condition_expression"),
                    )
                )

        cls.compiled_statements = compiled_statements

    def has_permission(self, request, view) -> bool:
        action = self._get_invoked_action(view)
        statements = self.get_policy_statements(request, view)

        if len(statements) == 0:
            return False

        allowed = self._evaluate_statements(statements, request, view, action)
        request.access_enforcement = AccessEnforcement(action=action, allowed=allowed)
        return allowed

    def get_policy_statements(self, request, view) -> List[Statement]:
        if self.compiled_statements:
            return self.compiled_statements

        raise AccessPolicyException(
            "get_policy_statements did not find any compiled statements to return"
        )

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
        self, statements: List[Statement], request, view, action: str
    ) -> bool:
        matched = self._get_statements_matching_principal(request, statements)
        matched = self._get_statements_matching_action(request, action, matched)

        matched = self._get_statements_matching_conditions(
            request, view, action=action, statements=matched, is_expression=False
        )

        matched = self._get_statements_matching_conditions(
            request, view, action=action, statements=matched, is_expression=True
        )

        denied = [_ for _ in matched if _.effect != "allow"]

        if len(matched) == 0 or len(denied) > 0:
            return False

        return True

    @classmethod
    def _get_statements_matching_principal(
        cls, request, statements: List[Statement]
    ) -> List[Statement]:
        user = request.user or AnonymousUser()
        user_roles = None
        matched = []

        for statement in statements:
            principals = statement.principal
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
        self, request, action: str, statements: List[Statement]
    ):
        """
        Filter statements and return only those that match the specified
        action.
        """
        matched = []
        SAFE_METHODS = ("GET", "HEAD", "OPTIONS")
        http_method = "<method:%s>" % request.method.lower()

        for statement in statements:
            if action in statement.action or "*" in statement.action:
                matched.append(statement)
            elif http_method in statement.action:
                matched.append(statement)
            elif (
                "<safe_methods>" in statement.action and request.method in SAFE_METHODS
            ):
                matched.append(statement)

        return matched

    def _get_statements_matching_conditions(
        self,
        request,
        view,
        *,
        action: str,
        statements: List[Statement],
        is_expression: bool,
    ) -> List[Statement]:
        """
        Filter statements and only return those that match all of their
        custom context conditions; if no conditions are provided then
        the statement should be returned.
        """
        matched = []

        for statement in statements:
            conditions = (
                statement.condition_expression if is_expression else statement.condition
            )

            if len(conditions) == 0:
                matched.append(statement)
                continue

            fails = 0

            for condition in conditions:
                if is_expression:
                    check_cond_fn = lambda cond: self._check_condition(
                        cond, request, view, action
                    )
                    bool_parser = get_parser(check_cond_fn)
                    passed = bool(bool_parser.parseString(condition)[0])
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
                "condition '%s' must return true/false, not %s"
                % (condition, type(result))
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
            "condition '%s' must be a method on the access policy or be defined in the 'reusable_conditions' module"
            % method_name
        )
