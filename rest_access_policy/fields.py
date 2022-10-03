import inspect
from typing import Type
from rest_framework import serializers

from .access_policy import AccessPolicy


class PermittedPkRelatedField(serializers.PrimaryKeyRelatedField):
    def __init__(self, access_policy: Type[AccessPolicy], **kwargs):
        self.access_policy = access_policy

        assert inspect.isclass(access_policy) and issubclass(
            access_policy, AccessPolicy
        ), "access_policy must be a subclass of AccessPolicy"

        super().__init__(**kwargs)

    def get_queryset(self):
        request = self.context.get("request")

        if not request:
            raise Exception(
                "When using PermittedPkRelatedField, "
                "the request must be passed in the serializer's context."
            )

        queryset = self.access_policy.scope_queryset(request, super().get_queryset())
        return queryset


class PermittedSlugRelatedField(serializers.SlugRelatedField):
    def __init__(self, access_policy: Type[AccessPolicy], **kwargs):
        self.access_policy = access_policy

        assert inspect.isclass(access_policy) and issubclass(
            access_policy, AccessPolicy
        ), "access_policy must be a subclass of AccessPolicy"

        super().__init__(**kwargs)

    def get_queryset(self):
        request = self.context.get("request")

        if not request:
            raise Exception(
                "When using PermittedSlugRelatedField, "
                "the request must be passed in the serializer's context."
            )

        queryset = self.access_policy.scope_queryset(request, super().get_queryset())
        return queryset
