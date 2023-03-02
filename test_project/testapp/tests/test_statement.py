from dataclasses import asdict
from rest_framework.test import APITestCase

from rest_access_policy import AccessViewSetMixin, AccessPolicy, Statement
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import AllowAny


class StatementTestCase(APITestCase):
    def test_should_raise_error_if_invalid_effect(self):
        with self.assertRaises(Exception) as context:
            Statement(principal="*", action="build", effect="veto")

        self.assertTrue("effect must be one of" in str(context.exception))

    def test_to_dict(self):
        statement = Statement(
            principal="*",
            action="build",
            effect="allow",
            condition_expression=["method1"],
        )

        self.assertEqual(
            asdict(statement),
            {
                "principal": "*",
                "action": "build",
                "effect": "allow",
                "condition": [],
                "condition_expression": ["method1"],
            },
        )
