from typing import List

from rest_framework.request import Request

from .access_policy import AccessPolicy


class FieldAccessMixin(object):
    def __init__(self, *args, **kwargs):
        self.serializer_context = kwargs.get("context", {})
        super().__init__(*args, **kwargs)
        self._apply_fields_access()
        self._apply_deprecated_field_permissions()

    @property
    def access_policy(self) -> AccessPolicy:
        meta = getattr(self, "Meta", None)

        if not meta:
            raise Exception("Must set access_policy inside Meta for FieldAccessMixin")

        access_policy = getattr(meta, "access_policy", None)

        if not access_policy:
            raise Exception("Must set access_policy inside Meta for FieldAccessMixin")

        if getattr(access_policy, "scope_fields", None) is None:
            raise Exception("Must define scope_fields method on access_policy")

        return access_policy

    @property
    def request(self) -> Request:
        request = self.serializer_context.get("request")

        if not request:
            raise Exception("Must pass context with request to FieldAccessMixin")

        return request

    def _apply_fields_access(self):
        fields = self.access_policy.scope_fields(self.request, self.fields, instance=self.instance)

        if fields is None:
            raise Exception("scope_fields method must return fields variable")

        self.fields = fields

    # Old style field-level permissions
    def _apply_deprecated_field_permissions(self):
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
    def field_permissions(self) -> dict:
        access_policy = self.access_policy
        field_permissions = getattr(access_policy, "field_permissions", {})

        if not isinstance(field_permissions, dict):
            raise Exception("Field permissions must be set on access_policy for FieldAccessMixin")

        return field_permissions

    def _set_read_only_fields(self):
        read_only_statements = self._validate_and_clean_statements(
            self.field_permissions["read_only"]
        )

        statements_matching_principal = self.access_policy._get_statements_matching_principal(
            request=self.request, statements=read_only_statements
        )

        for statement in statements_matching_principal:
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

        return statements
