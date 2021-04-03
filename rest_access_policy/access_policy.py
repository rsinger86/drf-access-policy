import importlib
from typing import List

from django.conf import settings
from django.db.models import prefetch_related_objects
from pyparsing import infixNotation, opAssoc
from rest_framework import permissions

from rest_access_policy import AccessPolicyException
from .parsing import ConditionOperand, boolOperand, BoolNot, BoolAnd, BoolOr


class AccessPolicy(permissions.BasePermission):
    statements = []
    id = None
    group_prefix = "group:"
    id_prefix = "id:"

    def has_permission(self, request, view) -> bool:
        action = self._get_invoked_action(view)
        statements = self.get_policy_statements(request, view)

        if len(statements) == 0:
            return False

        return self._evaluate_statements(statements, request, view, action)

    def get_policy_statements(self, request, view) -> List[dict]:
        return self.statements

    def get_user_group_values(self, user) -> List[str]:
        if user.is_anonymous:
            return []
        prefetch_related_objects([user], "groups")
        return [g.name for g in user.groups.all()]

    @classmethod
    def scope_queryset(cls, request, qs):
        return qs.none()

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
        self, statements: List[dict], request, view, action: str
    ) -> bool:
        statements = self._normalize_statements(statements)
        matched = self._get_statements_matching_principal(request, statements)
        matched = self._get_statements_matching_action(request, action, matched)

        matched = self._get_statements_matching_context_conditions(
            request, view, action, matched
        )

        denied = [_ for _ in matched if _["effect"] != "allow"]

        if len(matched) == 0 or len(denied) > 0:
            return False

        return True

    def _normalize_statements(self, statements=[]) -> List[dict]:
        for statement in statements:
            if isinstance(statement["principal"], str):
                statement["principal"] = [statement["principal"]]

            if isinstance(statement["action"], str):
                statement["action"] = [statement["action"]]

            if "condition" not in statement:
                statement["condition"] = []
            elif isinstance(statement["condition"], str):
                statement["condition"] = [statement["condition"]]

        return statements

    def _get_statements_matching_principal(
        self, request, statements: List[dict]
    ) -> List[dict]:
        user = request.user
        user_roles = None
        matched = []

        for statement in statements:
            principals = statement["principal"]
            found = False

            if "*" in principals:
                found = True
            elif "admin" in principals:
                found = user.is_superuser
            elif "staff" in principals:
                found = user.is_staff
            elif "authenticated" in principals:
                found = not user.is_anonymous
            elif "anonymous" in principals:
                found = user.is_anonymous
            elif self.id_prefix + str(user.pk) in principals:
                found = True
            else:
                if not user_roles:
                    user_roles = self.get_user_group_values(user)

                for user_role in user_roles:
                    if self.group_prefix + user_role in principals:
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
        http_method = "<method:%s>" % request.method.lower()

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

    def _get_statements_matching_context_conditions(
        self, request, view, action: str, statements: List[dict]
    ):
        """
            Filter statements and only return those that match all of their
            custom context conditions; if no conditions are provided then
            the statement should be returned.
        """
        matched = []

        for statement in statements:
            if len(statement["condition"]) == 0:
                matched.append(statement)
                continue

            fails = 0

            for condition in statement["condition"]:
                ConditionOperand.check_condition_fn = lambda _, cond: self._check_condition(
                    cond, request, view, action
                )
                boolOperand.setParseAction(ConditionOperand)

                boolExpr = infixNotation(
                    boolOperand,
                    [
                        ("not", 1, opAssoc.RIGHT, BoolNot),
                        ("and", 2, opAssoc.LEFT, BoolAnd),
                        ("or", 2, opAssoc.LEFT, BoolOr),
                    ],
                )

                passed = bool(boolExpr.parseString(condition)[0])

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
            module_path = settings.DRF_ACCESS_POLICY.get("reusable_conditions")

            if module_path:
                module = importlib.import_module(module_path)

                if hasattr(module, method_name):
                    return getattr(module, method_name)

        raise AccessPolicyException(
            "condition '%s' must be a method on the access policy or be defined in the 'reusable_conditions' module"
            % method_name
        )
