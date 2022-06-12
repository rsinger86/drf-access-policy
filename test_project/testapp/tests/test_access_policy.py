import unittest.mock as mock
from typing import Optional

from django.contrib.auth.models import AnonymousUser, Group, User
from django.test import TestCase
from rest_access_policy import AccessPolicy, AccessPolicyException, Statement
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet


class FakeRequest(object):
    def __init__(self, user: Optional[User], method: str = "GET"):
        self.user = user
        self.method = method


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

    def test_get_statements_matching_principal_if_user_is_authenticated(self):
        cooks = Group.objects.create(name="cooks")
        user = User.objects.create(id=5)
        user.groups.add(cooks)

        statements = [
            Statement.from_dict(
                {"principal": ["id:5"], "action": ["create"], "effect": "allow"}
            ),
            Statement.from_dict(
                {"principal": ["group:dev"], "action": ["destroy"], "effect": "allow"}
            ),
            Statement.from_dict(
                {
                    "principal": ["group:cooks"],
                    "action": ["do_something"],
                    "effect": "allow",
                }
            ),
            Statement.from_dict(
                {"principal": ["*"], "action": ["*"], "effect": "allow"}
            ),
            Statement.from_dict(
                {"principal": ["id:79"], "action": ["vote"], "effect": "allow"}
            ),
            Statement.from_dict(
                {
                    "principal": ["anonymous"],
                    "action": ["anonymous_action"],
                    "effect": "allow",
                }
            ),
            Statement.from_dict(
                {
                    "principal": ["authenticated"],
                    "action": ["authenticated_action"],
                    "effect": "allow",
                }
            ),
            Statement.from_dict(
                {"principal": ["staff"], "action": ["staff_action"], "effect": "allow"}
            ),
            Statement.from_dict(
                {"principal": ["admin"], "action": ["admin_action"], "effect": "allow"}
            ),
        ]

        policy = AccessPolicy()

        result = policy._get_statements_matching_principal(
            FakeRequest(user), statements
        )

        self.assertEqual(len(result), 4)
        self.assertEqual(result[0].action, ["create"])
        self.assertEqual(result[1].action, ["do_something"])
        self.assertEqual(result[2].action, ["*"])
        self.assertEqual(result[3].action, ["authenticated_action"])

    def test_get_statements_matching_principal_if_user_is_staff(self):
        cooks = Group.objects.create(name="cooks")
        user = User.objects.create(id=5)
        user.groups.add(cooks)
        user.is_staff = True
        user.save()

        statements = [
            Statement.from_dict(
                {"principal": ["id:5"], "action": ["create"], "effect": "allow"}
            ),
            Statement.from_dict(
                {"principal": ["group:dev"], "action": ["destroy"], "effect": "allow"}
            ),
            Statement.from_dict(
                {
                    "principal": ["group:cooks"],
                    "action": ["do_something"],
                    "effect": "allow",
                }
            ),
            Statement.from_dict(
                {"principal": ["*"], "action": ["*"], "effect": "allow"}
            ),
            Statement.from_dict(
                {"principal": ["id:79"], "action": ["vote"], "effect": "allow"}
            ),
            Statement.from_dict(
                {
                    "principal": ["anonymous"],
                    "action": ["anonymous_action"],
                    "effect": "allow",
                }
            ),
            Statement.from_dict(
                {
                    "principal": ["authenticated"],
                    "action": ["authenticated_action"],
                    "effect": "allow",
                }
            ),
            Statement.from_dict(
                {"principal": ["staff"], "action": ["staff_action"], "effect": "allow"}
            ),
            Statement.from_dict(
                {"principal": ["admin"], "action": ["admin_action"], "effect": "allow"}
            ),
        ]

        policy = AccessPolicy()

        result = policy._get_statements_matching_principal(
            FakeRequest(user), statements
        )

        self.assertEqual(len(result), 5)
        self.assertEqual(result[0].action, ["create"])
        self.assertEqual(result[1].action, ["do_something"])
        self.assertEqual(result[2].action, ["*"])
        self.assertEqual(result[3].action, ["authenticated_action"])
        self.assertEqual(result[4].action, ["staff_action"])

    def test_get_statements_matching_principal_if_user_is_admin(self):
        cooks = Group.objects.create(name="cooks")
        user = User.objects.create(id=5)
        user.groups.add(cooks)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        statements = [
            {"principal": ["id:5"], "action": ["create"]},
            {"principal": ["group:dev"], "action": ["destroy"]},
            {"principal": ["group:cooks"], "action": ["do_something"]},
            {"principal": ["*"], "action": ["*"]},
            {"principal": ["id:79"], "action": ["vote"]},
            {"principal": ["anonymous"], "action": ["anonymous_action"]},
            {"principal": ["authenticated"], "action": ["authenticated_action"]},
            {"principal": ["staff"], "action": ["staff_action"]},
            {"principal": ["admin"], "action": ["admin_action"]},
        ]

        policy = AccessPolicy()

        result = policy._get_statements_matching_principal(
            FakeRequest(user), statements
        )

        self.assertEqual(len(result), 6)
        self.assertEqual(result[0]["action"], ["create"])
        self.assertEqual(result[1]["action"], ["do_something"])
        self.assertEqual(result[2]["action"], ["*"])
        self.assertEqual(result[3]["action"], ["authenticated_action"])
        self.assertEqual(result[4]["action"], ["staff_action"])
        self.assertEqual(result[5]["action"], ["admin_action"])

    def test_get_statements_matching_principal_if_user_is_anonymous(self):
        user = AnonymousUser()

        statements = [
            Statement.from_dict(
                {"principal": ["id:5"], "action": ["create"], "effect": "allow"}
            ),
            Statement.from_dict(
                {"principal": ["*"], "action": ["list"], "effect": "allow"}
            ),
            Statement.from_dict(
                {
                    "principal": ["anonymous"],
                    "action": ["anonymous_action"],
                    "effect": "allow",
                }
            ),
            Statement.from_dict(
                {
                    "principal": ["authenticated"],
                    "action": ["authenticated_action"],
                    "effect": "allow",
                }
            ),
            Statement.from_dict(
                {"principal": ["staff"], "action": ["staff_action"], "effect": "allow"}
            ),
            Statement.from_dict(
                {"principal": ["admin"], "action": ["admin_action"], "effect": "allow"}
            ),
        ]

        policy = AccessPolicy()

        result = policy._get_statements_matching_principal(
            FakeRequest(user), statements
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].action, ["list"])
        self.assertEqual(result[1].action, ["anonymous_action"])

    def test_get_statements_matching_action_when_method_unsafe(self):
        cooks = Group.objects.create(name="cooks")
        user = User.objects.create(id=5)
        user.groups.add(cooks)

        statements = [
            {"principal": ["id:5"], "action": ["create"]},
            {"principal": ["group:dev"], "action": ["destroy"]},
            {"principal": ["group:cooks"], "action": ["do_something"]},
            {"principal": ["*"], "action": ["*"]},
            {"principal": ["id:79"], "action": ["vote"]},
            {"principal": ["id:900"], "action": ["<safe_methods>"]},
        ]

        policy = AccessPolicy()

        result = policy._get_statements_matching_action(
            FakeRequest(user, method="DELETE"), "destroy", statements
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["action"], ["destroy"])
        self.assertEqual(result[1]["action"], ["*"])

    def test_get_statements_matching_action_when_method_safe(self):
        cooks = Group.objects.create(name="cooks")
        user = User.objects.create(id=5)
        user.groups.add(cooks)

        statements = [
            {"principal": ["*"], "action": ["list"]},
            {"principal": ["id:5"], "action": ["*"]},
            {"principal": ["group:cooks"], "action": ["<safe_methods>"]},
            {"principal": ["group:devs"], "action": ["destroy"]},
        ]

        policy = AccessPolicy()

        result = policy._get_statements_matching_action(
            FakeRequest(user, method="GET"), "list", statements
        )

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["principal"], ["*"])
        self.assertEqual(result[1]["principal"], ["id:5"])
        self.assertEqual(result[2]["principal"], ["group:cooks"])

    def test_get_statements_matching_action_when_using_http_method_placeholder(self):
        cooks = Group.objects.create(name="cooks")
        user = User.objects.create(id=5)
        user.groups.add(cooks)

        statements = [
            {"principal": ["*"], "action": ["create"]},
            {"principal": ["group:cooks"], "action": ["<method:post>"]},
            {"principal": ["group:devs"], "action": ["destroy"]},
        ]

        policy = AccessPolicy()

        result = policy._get_statements_matching_action(
            FakeRequest(user, method="POST"), "an action that won't match", statements
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["principal"], ["group:cooks"])

    def test_get_statements_matching_conditions(self):
        class TestPolicy(AccessPolicy):
            def is_true(self, request, view, action):
                return True

            def is_false(self, request, view, action):
                return False

            def is_cloudy(self, request, view, action):
                return True

            def is_arg_true(self, request, view, action, arg):
                return eval(arg)

        statements = [
            {
                "principal": ["id:1"],
                "action": ["create"],
                "condition": [],
                "condition_expression": [],
            },
            {
                "principal": ["id:2"],
                "action": ["create"],
                "condition": ["is_true"],
                "condition_expression": [],
            },
            {
                "principal": ["id:4"],
                "action": ["create"],
                "condition": ["is_false"],
                "condition_expression": [],
            },
            {
                "principal": ["id:5"],
                "action": ["create"],
                "condition": [],
                "condition_expression": ["is_cloudy", "is_false and is_true"],
            },
            {
                "principal": ["id:6"],
                "action": ["create"],
                "condition": [],
                "condition_expression": ["is_false and is_true", "is_cloudy"],
            },
            {
                "principal": ["id:7"],
                "action": ["create"],
                "condition": [],
                "condition_expression": ["is_true or is_false"],
            },
            {
                "principal": ["id:8"],
                "action": ["create"],
                "condition": [],
                "condition_expression": ["is_true and not is_false"],
            },
            {
                "principal": ["id:9"],
                "action": ["create"],
                "condition": [],
                "condition_expression": ["not not is_true"],
            },
            {
                "principal": ["id:10"],
                "action": ["create"],
                "condition": [],
                "condition_expression": ["not (is_true and is_false)"],
            },
            {
                "principal": ["id:11"],
                "action": ["create"],
                "condition": [],
                "condition_expression": ["is_false or not is_true and is_cloudy"],
            },
            {
                "principal": ["id:12"],
                "action": ["create"],
                "condition": [],
                "condition_expression": ["is_false or not is_true or not is_cloudy"],
            },
            {
                "principal": ["id:13"],
                "action": ["create"],
                "condition": [],
                "condition_expression": ["is_false or not (is_true and is_cloudy)"],
            },
            {
                "principal": ["id:14"],
                "action": ["create"],
                "condition": [],
                "condition_expression": ["is_true or is_false or is_cloudy"],
            },
            {
                "principal": ["id:15"],
                "action": ["create"],
                "condition": [],
                "condition_expression": ["is_false or is_arg_true:True"],
            },
            {
                "principal": ["id:16"],
                "action": ["create"],
                "condition": [],
                "condition_expression": ["is_false or is_arg_true:False"],
            },
        ]

        policy = TestPolicy()

        result = policy._get_statements_matching_conditions(
            None, None, action=None, statements=statements, is_expression=True
        )

        result = policy._get_statements_matching_conditions(
            None, None, action=None, statements=result, is_expression=False
        )

        self.assertEqual(
            result,
            [
                {
                    "principal": ["id:1"],
                    "action": ["create"],
                    "condition": [],
                    "condition_expression": [],
                },
                {
                    "principal": ["id:2"],
                    "action": ["create"],
                    "condition": ["is_true"],
                    "condition_expression": [],
                },
                {
                    "principal": ["id:7"],
                    "action": ["create"],
                    "condition": [],
                    "condition_expression": ["is_true or is_false"],
                },
                {
                    "principal": ["id:8"],
                    "action": ["create"],
                    "condition": [],
                    "condition_expression": ["is_true and not is_false"],
                },
                {
                    "principal": ["id:9"],
                    "action": ["create"],
                    "condition": [],
                    "condition_expression": ["not not is_true"],
                },
                {
                    "principal": ["id:10"],
                    "action": ["create"],
                    "condition": [],
                    "condition_expression": ["not (is_true and is_false)"],
                },
                {
                    "principal": ["id:14"],
                    "action": ["create"],
                    "condition": [],
                    "condition_expression": ["is_true or is_false or is_cloudy"],
                },
                {
                    "principal": ["id:15"],
                    "action": ["create"],
                    "condition": [],
                    "condition_expression": ["is_false or is_arg_true:True"],
                },
            ],
        )

    @mock.patch("rest_access_policy.access_policy.get_parser")
    def test_complex_condition_parser_not_called_for_simple_condition(
        self, get_parser_mock
    ):
        class TestPolicy(AccessPolicy):
            def is_cloudy(self, request, view, action):
                return True

        statements = [
            {
                "principal": ["id:1"],
                "action": ["create"],
                "condition": ["is_cloudy"],
                "condition_expression": [],
            }
        ]

        policy = TestPolicy()

        result = policy._get_statements_matching_conditions(
            None, None, action=None, statements=statements, is_expression=False
        )

        self.assertEqual(result, statements)
        get_parser_mock.assert_not_called()

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

    def test_check_condition_is_called_with_custom_arg(self):
        class TestPolicy(AccessPolicy):
            def user_is(self, request, view, action, field_name: str):
                return True if field_name == "owner" else False

        policy = TestPolicy()

        self.assertTrue(policy._check_condition("user_is:owner", None, None, "action"))
        self.assertFalse(policy._check_condition("user_is:staff", None, None, "action"))

    def test_check_condition_in_reusable_module_is_called(self):
        class TestPolicy(AccessPolicy):
            pass

        policy = TestPolicy()

        self.assertTrue(
            policy._check_condition("is_a_cat:Garfield", None, None, "action")
        )
        self.assertFalse(
            policy._check_condition("is_a_cat:Snoopy", None, None, "action")
        )

    def test_get_condition_method_from_self(self):
        class TestPolicy(AccessPolicy):
            def is_a_cat(self, request, view, action):
                return False

        policy = TestPolicy()

        self.assertEqual(policy._get_condition_method("is_a_cat"), policy.is_a_cat)

    def test_get_condition_method_from_reusable_module(self):
        class TestPolicy(AccessPolicy):
            pass

        policy = TestPolicy()
        from test_project import global_access_conditions

        self.assertEqual(
            policy._get_condition_method("is_a_cat"), global_access_conditions.is_a_cat
        )

    def test_get_condition_method_throw_error(self):
        class TestPolicy(AccessPolicy):
            pass

        policy = TestPolicy()

        with self.assertRaises(AccessPolicyException) as context:
            policy._get_condition_method("is_a_dog")

        self.assertTrue(
            "must be a method on the access policy or be defined in the 'reusable_conditions' module"
            in str(context.exception)
        )

    def test_evaluate_statements_false_if_no_statements(
        self,
    ):
        class TestPolicy(AccessPolicy):
            def is_sunny(self, request, view, action):
                return True

        policy = TestPolicy()
        user = User.objects.create(username="mr user")

        result = policy._evaluate_statements([], FakeRequest(user), None, "create")
        self.assertFalse(result)

    def test_evaluate_statements_false_any_deny(
        self,
    ):
        policy = AccessPolicy()
        user = User.objects.create(username="mr user")

        statements = [
            {"principal": "*", "action": "*", "effect": "deny"},
            {"principal": "*", "action": "*", "effect": "allow"},
        ]

        result = policy._evaluate_statements([], FakeRequest(user), None, "create")
        self.assertFalse(result)

    def test_evaluate_statements_true_if_any_allow_and_none_deny(
        self,
    ):
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
                [Statement(principal="*", action="create", effect="allow")],
                request,
                view,
                "create",
            )

    def test_has_permission_with_custom_condition_and_star_character(self):
        class TestPolicy(AccessPolicy):
            statements = [
                {
                    "action": "*",
                    "principal": "group:hr",
                    "effect": "allow",
                    "condition": ["check_permissions:*"],
                },
                {
                    "action": "*",
                    "principal": "group:admin",
                    "effect": "allow",
                    "condition": ["check_permissions:reboot"],
                },
            ]

            def check_permissions(self, request, view, action, permissions: str):
                if permissions == "*":
                    return True
                else:
                    return False

        policy = TestPolicy()
        view = FakeViewSet(action="create")

        fred = User.objects.create(username="fred")
        fred.groups.add(Group.objects.create(name="admin"))

        jane = User.objects.create(username="jane")
        jane.groups.add(Group.objects.create(name="hr"))

        self.assertFalse(policy.has_permission(FakeRequest(user=fred), view))
        self.assertTrue(policy.has_permission(FakeRequest(user=jane), view))

    def test_has_permission_is_true_when_user_is_none(self):
        class TestPolicy(AccessPolicy):
            statements = [{"action": "*", "principal": "anonymous", "effect": "allow"}]

        view = FakeViewSet(action="create")
        policy = TestPolicy()

        self.assertTrue(policy.has_permission(FakeRequest(user=None), view))

    def test_has_permission_is_false_when_user_is_none(self):
        class TestPolicy(AccessPolicy):
            statements = [
                {"action": "*", "principal": "authenticated", "effect": "allow"}
            ]

        view = FakeViewSet(action="create")
        policy = TestPolicy()
        self.assertFalse(policy.has_permission(FakeRequest(user=None), view))
