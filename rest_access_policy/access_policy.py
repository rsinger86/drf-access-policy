from typing import List

from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class AccessPolicy(permissions.BasePermission):
    statements = []
    id = None
    role_prefix = "role:"
    id_prefix = "id:"
    debug = False

    def has_permission(self, request, view):
        action = self._get_invoked_action(view)
        statements = self.get_policy_statements(request, view)

        if len(statements) == 0:
            return False

        return self._evaluate_statements(statements, request, view, action)

    def get_policy_statements(self, request, view) -> List[dict]:
        return self.statements

    def get_user_roles(self, user) -> List[str]:
        return user.groups.values_list("name", flat=True)

    @classmethod
    def scope_queryset(cls, request, qs):
        return qs.none()

    def _get_invoked_action(self, view):
        """
            If a CBV, the name of the method. If a regular function view,
            the name of the function.
        """
        if hasattr(view, "action"):
            return view.action
        elif hasattr(view, "__class__"):
            return view.__class__.__name__
        return None

    def _evaluate_statements(self, statements: List, request, view, action: str):
        statements = self._normalize_statements(statements)
        matched = self._get_statements_matching_principal(request, statements)
        matched = self._get_statements_matching_action(action, matched)

        matched = self._get_statements_matching_context_conditions(
            request, view, action, matched
        )

        allowed = [s for s in matched if s["effect"] == "allow"]

        if len(matched) == 0 or len(allowed) != len(matched):
            return False

        return True

    def _normalize_statements(self, statements=[]) -> List[dict]:
        for statement in statements:
            if isinstance(statement["principal"], str):
                statement["principal"] = [statement["principal"]]

            if isinstance(statement["action"], str):
                statement["action"] = [statement["action"]]

            if "custom_context_condition" not in statement:
                statement["custom_context_condition"] = []
            elif isinstance(statement["custom_context_condition"], str):
                statement["custom_context_condition"] = [
                    statement["custom_context_condition"]
                ]

        return statements

    def _get_statements_matching_principal(self, request, statements: List[dict]):
        user_roles = self.get_user_roles()
        principals = statement["principal"]
        matched = []

        for statement in statements:
            found = False

            if "*" in principals:
                found = True
            elif self.id_prefix + user.id in principals:
                found = True
            else:
                for user_role in user_roles:
                    if self.role_prefix + user_role in principals:
                        found = True
                        break

            if found:
                matched.append(statement)

        return matched

    def _get_statements_matching_action(self, action: str, statements: List):
        """
            Filter statements and return only those that match the specified
            action.
        """
        return [
            statement
            for statement in statements
            if action in statement["action"] or "*" in statement["action"]
        ]

    def _get_statements_matching_context_conditions(
        self, request, view, action: str, statements: List
    ):
        """
            Filter statements and only return those that match all of their
            custom context conditions; if no conditions are provided then
            the statement should be returned.
        """
        matched = []

        for statement in statements:
            if len(statement["custom_context_condition"]) == 0:
                matched.append(statement)
                continue

            fails = 0

            for condition in statement["custom_context_condition"]:
                passed = self._check_custom_context_condition(
                    condition, request, view, action
                )

                if not passed:
                    fails += 1
                    break

            if fails == 0:
                matched.append(statement)

        return matched

    def _check_custom_context_condition(
        self, condition: str, request, view, action: str
    ):
        """
            Evaluate a custom context condition; if method does not exist on
            the access policy class, then return False.
        """
        if not hasattr(self, condition):
            return False

        method = getattr(self, condition)
        return method(request, view, action)
