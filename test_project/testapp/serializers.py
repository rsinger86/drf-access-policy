from rest_framework import serializers
from test_project.testapp.models import UserAccount


class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ["username", "first_name", "last_name"]
