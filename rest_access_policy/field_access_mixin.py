from typing import List

from rest_framework.request import Request

from rest_access_policy import AccessPolicyException
from .access_policy import AccessPolicy


class FieldAccessMixin(object):
    def __init__(self, *args, **kwargs):
        self.serializer_context = kwargs.get("context", {})
        is_many = kwargs.get('many', False)
        super().__init__(*args, **kwargs)
        self.should_check_conditions =  is_many is False and getattr(self,"instance",None) is not None

        if (
            self.request.method
            in [
                "POST",
                "PUT",
                "PATCH",
            ]
            and self.field_permissions.get("read_only")
        ):
            self._set_read_only_fields()

    @property
    def access_policy(self) -> AccessPolicy:
        meta = getattr(self, "Meta", None)

        if not meta:
            raise Exception("Must set access_policy inside Meta for FieldAccessMixin")

        access_policy = getattr(meta, "access_policy", None)

        if not access_policy:
            raise Exception("Must set access_policy inside Meta for FieldAccessMixin")

        return access_policy

    @property
    def request(self) -> Request:
        request = self.serializer_context.get("request")

        if not request:
            raise Exception("Must pass context with request to FieldAccessMixin")

        return request

    @property
    def action(self) -> Request:
        view = self.serializer_context.get("view")
        if not view:
            raise Exception("Must pass context with view to FieldAccessMixin")
        action = self.access_policy._get_invoked_action(view)
        return action


    @property
    def field_permissions(self) -> dict:
        access_policy = self.access_policy

        field_permissions = getattr(access_policy, "field_permissions", {})

        if not isinstance(field_permissions, dict):
            raise Exception("Field permissions must be set on access_policy for FieldAccessMixin")

        return field_permissions

    def _get_statements_matching_conditions(self,  statements: List[dict]):
        """
        Filter statements and only return those that match all of their
        custom context conditions; if no conditions are provided then
        the statement should be returned.
        """
        matched = []

        for statement in statements:
            conditions = statement["condition"]

            if len(conditions) == 0:
                matched.append(statement)
                continue

            fails = 0

            for condition in conditions:
                passed = self._check_condition(condition)

                if not passed:
                    fails += 1
                    break

            if fails == 0:
                matched.append(statement)

        return matched

    def _get_statements_matching_action(self, statements: List[dict]):
        """
        Filter statements and return only those that match the specified
        action.
        """
        matched = []
        http_method = "<method:%s>" % self.request.method.lower()

        for statement in statements:
            if self.action in statement["action"] or "*" in statement["action"]:
                matched.append(statement)
            elif http_method in statement["action"]:
                matched.append(statement)
        return matched

    def _check_condition(self, condition):
        """
        Evaluate a custom context condition;
        """
        result = condition(self.instance)

        if type(result) is not bool:
            raise AccessPolicyException(
                "condition '%s' must return true/false, not %s" % (condition, type(result))
            )

        return result

    def _set_read_only_fields(self):
        read_only_statements = self._validate_and_clean_statements(
            self.field_permissions["read_only"]
        )

        matched = self.access_policy._get_statements_matching_principal(
            request=self.request, statements=read_only_statements
        )
        matched = self._get_statements_matching_action(statements=matched)
        if self.should_check_conditions:
            matched = self._get_statements_matching_conditions(statements=matched)
        for statement in matched:
            if "*" in statement["fields"]:
                for field in self.fields.values():
                    field.read_only = True
                break
            else:
                for field in statement["fields"]:
                    if self.fields.get(field, None) is not None:
                        self.fields[field].read_only = True

    def _validate_and_clean_statements(self, statements: List[dict]) -> List[dict]:
        for statement in statements:
            if not isinstance(statement, dict):
                raise Exception("Must pass a dict as statement")

            if len(statement) == 0:
                raise Exception("Cannot pass empty dict as statement")

            if statement.get("principal", None) is None:
                raise Exception("Must pass principal in statement")

            if statement.get("fields", None) is None:
                raise Exception("Must pass fields in statement")

            if isinstance(statement["principal"], str):
                statement["principal"] = [statement["principal"]]

            if isinstance(statement["fields"], str):
                statement["fields"] = [statement["fields"]]

            if "action" not in statement:
                statement["action"] = ["*"]

            if isinstance(statement["action"], str):
                statement["action"] = [statement["action"]]

            if "condition" not in statement:
                statement["condition"] = []
            elif callable(statement["condition"]):
                statement["condition"] = [statement["condition"]]

        return statements
