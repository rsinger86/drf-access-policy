from rest_framework.test import APITestCase

from rest_access_policy import AccessViewSetMixin, AccessPolicy
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import AllowAny


class AccessViewSetTestCase(APITestCase):
    def test_should_raise_error_if_no_access_policy_set(self):
        class MyViewSet(AccessViewSetMixin, ViewSet):
            pass

        with self.assertRaises(Exception) as context:
            v = MyViewSet()

        self.assertTrue("you must assign an AccessPolicy " in str(context.exception))

    def test_should_not_raise_error_if_access_policy_set(self):
        class MyViewSet(AccessViewSetMixin, ViewSet):
            access_policy = AccessPolicy

        v = MyViewSet()

    def test_prepend_policy_to_permissions_without_modifying_class_attribute(self):
        class MyViewSet(AccessViewSetMixin, ViewSet):
            access_policy = AccessPolicy

        v = MyViewSet()
        self.assertEqual(v.permission_classes, [AccessPolicy, AllowAny])
        self.assertEqual(MyViewSet.permission_classes, [AllowAny])
