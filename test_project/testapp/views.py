from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from test_project.testapp.access_policies import (
    LogsAccessPolicy,
    UserAccountAccessPolicy,
)
from test_project.testapp.models import UserAccount
from test_project.testapp.serializers import UserAccountSerializer


class UserAccountViewSet(viewsets.ModelViewSet):
    permission_classes = (UserAccountAccessPolicy,)
    serializer_class = UserAccountSerializer
    queryset = UserAccount.objects.all()


@api_view(["GET"])
@permission_classes((LogsAccessPolicy,))
def get_logs(request):
    return Response({"status": "OK"})


@api_view(["DELETE"])
@permission_classes((LogsAccessPolicy,))
def delete_logs(request):
    return Response({"status": "OK"})
