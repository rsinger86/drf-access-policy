from django.test import TestCase
from rest_access_policy import AccessPolicy


class AccessPolicyTests(TestCase):
    def test_decorate_with_multiple_hooks(self):
        print("hi")
