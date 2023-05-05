from typing import Optional
from rest_framework.test import APITestCase, APIRequestFactory
from django.contrib.auth.models import User

from rest_access_policy import AccessPolicy
from rest_access_policy import PermittedPkRelatedField, PermittedSlugRelatedField
from rest_framework.serializers import Serializer

from rest_access_policy.fields import PermittedHyperlinkedRelatedField
from test_project.testapp.serializers import UserAccountHyperlinkedSerializer


class FakeRequest(object):
    def __init__(self, user: Optional[User], method: str = "GET"):
        self.user = user
        self.method = method


class FieldsTestCase(APITestCase):
    def test_include_in_scope_object(self):
        class TestPolicy(AccessPolicy):
            @classmethod
            def scope_queryset(cls, request, queryset):
                return queryset

        class TestSerializer(Serializer):
            user = PermittedPkRelatedField(
                access_policy=TestPolicy, queryset=User.objects.all()
            )

        request_user = User.objects.create(username="Requester")

        user = User.objects.create(username="Test user")

        serializer = TestSerializer(
            data={"user": user.pk}, context={"request": FakeRequest(user=request_user)}
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["user"], user)

    def test_exclude_out_of_scope_object(self):
        request_user = User.objects.create(username="Requester")

        user = User.objects.create(username="Test user")

        class TestPolicy(AccessPolicy):
            @classmethod
            def scope_queryset(cls, request, queryset):
                if request.user == request_user:
                    return queryset.none()
                return queryset

        class TestSerializer(Serializer):
            user = PermittedPkRelatedField(
                access_policy=TestPolicy, queryset=User.objects.all()
            )

        serializer = TestSerializer(
            data={"user": user.pk}, context={"request": FakeRequest(user=request_user)}
        )

        self.assertFalse(serializer.is_valid())
        self.assertTrue("object does not exist" in str(serializer.errors))


class SlugFieldsTestCase(APITestCase):
    def test_include_in_scope_object(self):
        class TestPolicy(AccessPolicy):
            @classmethod
            def scope_queryset(cls, request, queryset):
                return queryset

        class TestSerializer(Serializer):
            user = PermittedSlugRelatedField(
                access_policy=TestPolicy, queryset=User.objects.all(), slug_field="username"
            )

        request_user = User.objects.create(username="Requester")

        user = User.objects.create(username="Test user")

        serializer = TestSerializer(
            data={"user": "Test user"}, context={"request": FakeRequest(user=request_user)}
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["user"], user)

    def test_exclude_out_of_scope_object(self):
        request_user = User.objects.create(username="Requester")

        user = User.objects.create(username="Test user")

        class TestPolicy(AccessPolicy):
            @classmethod
            def scope_queryset(cls, request, queryset):
                if request.user == request_user:
                    return queryset.none()
                return queryset

        class TestSerializer(Serializer):
            user = PermittedSlugRelatedField(
                access_policy=TestPolicy, queryset=User.objects.all(), slug_field="username"
            )

        serializer = TestSerializer(
            data={"user": "Test user"}, context={"request": FakeRequest(user=request_user)}
        )

        self.assertFalse(serializer.is_valid())
        self.assertTrue("Object with username=Test user does not exist" in str(serializer.errors))


class HyperlinkedFieldsTestCase(APITestCase):
    def test_include_in_scope_object(self):
        class TestPolicy(AccessPolicy):
            @classmethod
            def scope_queryset(cls, request, queryset):
                return queryset

        class TestSerializer(Serializer):
            user = PermittedHyperlinkedRelatedField(
                access_policy=TestPolicy, queryset=User.objects.all(), view_name="account-hyperlinked-test-detail"
            )

        request_user = User.objects.create(username="Requester")

        factory = APIRequestFactory()
        request = factory.get('/accounts-hyperlinked-test/')
        request.user = request_user

        user = User.objects.create(username="Test user")
        user_url = UserAccountHyperlinkedSerializer(user, context={"request": request}).data["url"]

        serializer = TestSerializer(
            data={"user": user_url}, context={"request": request}
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["user"], user)

    def test_exclude_out_of_scope_object(self):
        request_user = User.objects.create(username="Requester")

        factory = APIRequestFactory()
        request = factory.get('/accounts-hyperlinked-test/')
        request.user = request_user

        user = User.objects.create(username="Test user")
        user_url = UserAccountHyperlinkedSerializer(user, context={"request": request}).data["url"]

        class TestPolicy(AccessPolicy):
            @classmethod
            def scope_queryset(cls, request, queryset):
                if request.user == request_user:
                    return queryset.none()
                return queryset

        class TestSerializer(Serializer):
            user = PermittedHyperlinkedRelatedField(
                access_policy=TestPolicy, queryset=User.objects.all(), view_name="account-hyperlinked-test-detail"
            )

        serializer = TestSerializer(
            data={"user": user_url}, context={"request": request}
        )

        self.assertFalse(serializer.is_valid())
        self.assertTrue("Invalid hyperlink" in str(serializer.errors))
