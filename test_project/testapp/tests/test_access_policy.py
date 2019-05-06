import unittest.mock as mock

from django.contrib.auth.models import AnonymousUser, Group, User
from django.test import TestCase
from rest_access_policy import AccessPolicy, AccessPolicyException
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet


class FakeRequest(object):
    def __init__(self, user: User):
        self.user = user


class FakeViewSet(object):
    def __init__(self, action: str = "create"):
        self.action = action


class AccessPolicyTests(TestCase):
    def setUp(self):
        User.objects.all().delete()
        Group.objects.all().delete()

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

    def test_get_user_group_values(self):
        group1 = Group.objects.create(name="admin")
        group2 = Group.objects.create(name="ceo")
        user = User.objects.create(username="mr user")

        user.groups.add(group1, group2)

        policy = AccessPolicy()
        result = sorted(policy.get_user_group_values(user))

        self.assertEqual(result, ["admin", "ceo"])

    def test_get_user_group_values_empty_if_user_is_anonymous(self):
        user = AnonymousUser()
        policy = AccessPolicy()
        result = sorted(policy.get_user_group_values(user))
        self.assertEqual(result, [])

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

    def test_get_statements_matching_principal(self):
        cooks = Group.objects.create(name="cooks")
        user = User.objects.create(id=5)
        user.groups.add(cooks)

        statements = [
            {"principal": ["id:5"], "action": ["create"]},
            {"principal": ["group:dev"], "action": ["delete"]},
            {"principal": ["group:cooks"], "action": ["do_something"]},
            {"principal": ["*"], "action": ["*"]},
            {"principal": ["id:79"], "action": ["vote"]},
        ]

        policy = AccessPolicy()

        result = policy._get_statements_matching_principal(
            FakeRequest(user), statements
        )

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["action"], ["create"])
        self.assertEqual(result[1]["action"], ["do_something"])
        self.assertEqual(result[2]["action"], ["*"])

    def test_get_statements_matching_principal_if_user_is_anonymous(self):
        user = AnonymousUser()

        statements = [
            {"principal": ["id:5"], "action": ["create"]},
            {"principal": ["*"], "action": ["list"]},
        ]

        policy = AccessPolicy()

        result = policy._get_statements_matching_principal(
            FakeRequest(user), statements
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["action"], ["list"])

    def test_get_statements_matching_action(self):
        cooks = Group.objects.create(name="cooks")
        user = User.objects.create(id=5)
        user.groups.add(cooks)

        statements = [
            {"principal": ["id:5"], "action": ["create"]},
            {"principal": ["group:dev"], "action": ["delete"]},
            {"principal": ["group:cooks"], "action": ["do_something"]},
            {"principal": ["*"], "action": ["*"]},
            {"principal": ["id:79"], "action": ["vote"]},
        ]

        policy = AccessPolicy()

        result = policy._get_statements_matching_action("delete", statements)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["action"], ["delete"])
        self.assertEqual(result[1]["action"], ["*"])

    def test_get_statements_matching_context_conditions(self):
        class TestPolicy(AccessPolicy):
            def is_sunny(self, request, view, action):
                return True

            def is_cloudy(self, request, view, action):
                return False

        statements = [
            {"principal": ["id:1"], "action": ["create"], "condition": []},
            {"principal": ["id:2"], "action": ["create"], "condition": ["is_sunny"]},
            {"principal": ["id:3"], "action": ["create"], "condition": ["is_cloudy"]},
        ]

        policy = TestPolicy()

        result = policy._get_statements_matching_context_conditions(
            None, None, None, statements
        )

        self.assertEqual(
            result,
            [
                {"principal": ["id:1"], "action": ["create"], "condition": []},
                {
                    "principal": ["id:2"],
                    "action": ["create"],
                    "condition": ["is_sunny"],
                },
            ],
        )

    def test_check_condition_throws_error_if_no_method(self):
        class TestPolicy(AccessPolicy):
            pass

        policy = TestPolicy()

        with self.assertRaises(AccessPolicyException) as context:
            policy._check_condition("is_sunny", None, None, "action")

        self.assertTrue(
            "condition 'is_sunny' must be a method on the access policy"
            in str(context.exception)
        )

    def test_check_condition_throws_error_if_returns_non_boolean(self):
        class TestPolicy(AccessPolicy):
            def is_sunny(self, request, view, action):
                return "yup"

        policy = TestPolicy()

        with self.assertRaises(AccessPolicyException) as context:
            policy._check_condition("is_sunny", None, None, "action")

        self.assertTrue(
            "condition 'is_sunny' must return true/false, not" in str(context.exception)
        )

    def test_check_condition_is_called(self):
        class TestPolicy(AccessPolicy):
            def is_sunny(self, request, view, action):
                return True

        policy = TestPolicy()

        self.assertTrue(policy._check_condition("is_sunny", None, None, "action"))

    def test_evaluate_statements_false_if_no_statements(self,):
        class TestPolicy(AccessPolicy):
            def is_sunny(self, request, view, action):
                return True

        policy = TestPolicy()
        user = User.objects.create(username="mr user")

        result = policy._evaluate_statements([], FakeRequest(user), None, "create")
        self.assertFalse(result)

    def test_evaluate_statements_false_any_deny(self,):
        policy = AccessPolicy()
        user = User.objects.create(username="mr user")

        statements = [
            {"principal": "*", "action": "*", "effect": "deny"},
            {"principal": "*", "action": "*", "effect": "allow"},
        ]

        result = policy._evaluate_statements([], FakeRequest(user), None, "create")
        self.assertFalse(result)

    def test_evaluate_statements_true_if_any_allow_and_none_deny(self,):
        policy = AccessPolicy()
        user = User.objects.create(username="mr user")

        statements = [
            {"principal": "*", "action": "create", "effect": "allow"},
            {"principal": "*", "action": "take_out_the_trash", "effect": "allow"},
        ]

        result = policy._evaluate_statements(
            statements, FakeRequest(user), None, "create"
        )
        self.assertTrue(result)

    def test_has_permission(self):
        class TestPolicy(AccessPolicy):
            statements = [{"principal": "*", "action": "create", "effect": "allow"}]

            def is_sunny(self, request, view, action):
                return True

        policy = TestPolicy()
        view = FakeViewSet(action="create")
        request = FakeRequest(user=User.objects.create(username="fred"))

        with mock.patch.object(
            policy, "_evaluate_statements", wraps=policy._evaluate_statements
        ) as monkey:
            policy.has_permission(request, view)
            monkey.assert_called_with(
                [
                    {
                        "principal": ["*"],
                        "action": ["create"],
                        "effect": "allow",
                        "condition": [],
                    }
                ],
                request,
                view,
                "create",
            )
