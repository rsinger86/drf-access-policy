from typing import List

from rest_framework.request import Request

from .access_policy import AccessPolicy


class FieldAccessMixin(object):
    def __init__(self, *args, **kwargs):
        self.serializer_context = kwargs.get("context", {})
        super().__init__(*args, **kwargs)
        self._apply_access_policy()

    @property
    def access_policy(self) -> AccessPolicy:
        meta = getattr(self, "Meta", None)

        if not meta:
            raise Exception("Must set access_policy inside Meta for FieldAccessMixin")

        access_policy = getattr(meta, "access_policy", None)

        if not access_policy:
            raise Exception("Must set access_policy inside Meta for FieldAccessMixin")

        if getattr(access_policy,"scope_fields",None) is None:
            raise Exception("Must define scope_fields method on access_policy")

        return access_policy

    @property
    def request(self) -> Request:
        request = self.serializer_context.get("request")

        if not request:
            raise Exception("Must pass context with request to FieldAccessMixin")

        return request

    def _apply_access_policy(self):
        fields = self.access_policy.scope_fields(self.request, self.fields, instance=self.instance)
        if fields is None:
            raise Exception("scope_fields method must return fields variable")

        self.fields = self.access_policy.scope_fields(self.request, self.fields, instance=self.instance)

    