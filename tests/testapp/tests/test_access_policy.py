from django.test import TestCase
from django.contrib.auth.models import User, Group
from rest_access_policy import AccessPolicy
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet


class AccessPolicyTests(TestCase):
    def test_get_invoked_action_from_function_based_view(self):
        @api_view(["GET"])
        def my_view(request):
            return ""

        policy = AccessPolicy()
        view_instance = my_view.cls()

        result = policy._get_invoked_action(view_instance)
        self.assertEqual(result, "my_view")

    def test_get_invoked_action_from_class_based_view(self):
        class UserViewSet(ModelViewSet):
            pass

        policy = AccessPolicy()
        view_instance = UserViewSet()
        view_instance.action = "create"

        result = policy._get_invoked_action(view_instance)
        self.assertEqual(result, "create")

    def test_get_user_groups(self):
        group1 = Group.objects.create(name="admin")
        group2 = Group.objects.create(name="ceo")
        user = User.objects.create(username="mr user")

        user.groups.add(group1, group2)

        policy = AccessPolicy()
        result = sorted(policy.get_user_groups(user))

        self.assertEqual(result, ["admin", "ceo"])
        Group.objects.all().delete()
        user.delete()

    def test_normalize_statements(self):
        policy = AccessPolicy()

        result = policy._normalize_statements(
            [
                {
                    "principal": "group:admin",
                    "action": "delete",
                    "condition": "is_nice_day",
                }
            ]
        )

        self.assertEqual(
            result,
            [
                {
                    "principal": ["group:admin"],
                    "action": ["delete"],
                    "condition": ["is_nice_day"],
                }
            ],
        )
