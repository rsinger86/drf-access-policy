import inspect
from typing import Type

from rest_access_policy import AccessPolicy
from rest_framework.response import Response


class AccessViewSetMixin(object):
    access_policy: Type[AccessPolicy]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        access_policy = getattr(self, "access_policy", None)

        if not inspect.isclass(access_policy) or not issubclass(access_policy, AccessPolicy):
            raise Exception(
                """
                    When mixing AccessViewSetMixin into your view set, you must assign an AccessPolicy 
                    to the access_policy class attribute.
                """
            )

        self.permission_classes = [self.access_policy] + self.permission_classes

    def finalize_response(self, request, response, *args, **kwargs) -> Response:
        response = super().finalize_response(request, response, *args, **kwargs)
        return response
