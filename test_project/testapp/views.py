from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from test_project.testapp.access_policies import UserAccountAccessPolicy
from test_project.testapp.models import UserAccount
from test_project.testapp.serializers import UserAccountSerializer


class UserAccountViewSet(viewsets.ModelViewSet):
    """
    API endpoint for testing purposes.
    """

    permission_classes = (UserAccountAccessPolicy,)
    serializer_class = UserAccountSerializer
    queryset = UserAccount.objects.all()
