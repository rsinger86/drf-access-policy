from rest_access_policy import access_policy
from rest_framework import serializers
from test_project.testapp.models import UserAccount
from test_project.testapp.access_policies import UserAccountAccessPolicy
from rest_access_policy.field_access_mixin import FieldAccessMixin


class UserAccountSerializer(FieldAccessMixin, serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ["username", "first_name", "last_name", "status"]
        access_policy = UserAccountAccessPolicy


class UserAccountHyperlinkedSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="account-hyperlinked-test-detail")

    class Meta:
        model = UserAccount
        fields = ["url", "username", "first_name", "last_name", "status"]
