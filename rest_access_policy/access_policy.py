from typing import List

from rest_framework import permissions
from rest_access_policy import AccessPolicyException


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
        return list(user.groups.values_list("name", flat=True))

    @classmethod
    def scope_queryset(cls, request, qs):
        return qs.none()

    def _get_invoked_action(self, view) -> str:
        """
            If a CBV, the name of the method. If a regular function view,
            the name of the function.
        """
        if hasattr(view, "action"):
            return view.action
        elif hasattr(view, "__class__"):
            return view.__class__.__name__
        raise AccessPolicyException("Could not determine action of request")

    def _evaluate_statements(
        self, statements: List[dict], request, view, action: str
    ) -> bool:
        statements = self._normalize_statements(statements)
        matched = self._get_statements_matching_principal(request, statements)
        matched = self._get_statements_matching_action(action, matched)

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
        user_roles = self.get_user_group_values(user)
        matched = []

        for statement in statements:
            principals = statement["principal"]
            found = False

            if "*" in principals:
                found = True
            elif "authenticated" in principals:
                found = not user.is_anonymous
            elif "anonymous" in principals:
                found = user.is_anonymous
            elif self.id_prefix + str(user.id) in principals:
                found = True
            else:
                for user_role in user_roles:
                    if self.group_prefix + user_role in principals:
                        found = True
                        break

            if found:
                matched.append(statement)

        return matched

    def _get_statements_matching_action(self, action: str, statements: List[dict]):
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
        """
        if not hasattr(self, condition):
            raise AccessPolicyException(
                "condition '%s' must be a method on the access policy" % condition
            )

        method = getattr(self, condition)
        result = method(request, view, action)

        if type(result) is not bool:
            raise AccessPolicyException(
                "condition '%s' must return true/false, not %s"
                % (condition, type(result))
            )

        return result
