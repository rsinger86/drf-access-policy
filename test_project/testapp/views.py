from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from test_project.testapp.access_policies import (
    LogsAccessPolicy,
    UserAccountAccessPolicy,
    LandingPageAccessPolicy,
)
from test_project.testapp.models import UserAccount
from test_project.testapp.serializers import UserAccountSerializer, UserAccountHyperlinkedSerializer
from rest_access_policy import AccessViewSetMixin


class UserAccountViewSetWithMixin(AccessViewSetMixin, viewsets.ModelViewSet):
    access_policy = UserAccountAccessPolicy
    serializer_class = UserAccountSerializer
    queryset = UserAccount.objects.all()

    @action(detail=True, methods=["post"])
    def set_password(self, request, pk=None):
        return Response({}, status=200)


class UserAccountViewSet(viewsets.ModelViewSet):
    permission_classes = (UserAccountAccessPolicy,)
    serializer_class = UserAccountSerializer
    queryset = UserAccount.objects.all()

    @action(detail=True, methods=["post"])
    def set_password(self, request, pk=None):
        return Response({}, status=200)


class UserAccountHyperlinkedViewSet(viewsets.ModelViewSet):
    serializer_class = UserAccountHyperlinkedSerializer
    queryset = UserAccount.objects.all()


@api_view(["GET"])
@permission_classes((LogsAccessPolicy,))
def get_logs(request):
    return Response({"status": "OK"})


@api_view(["DELETE"])
@permission_classes((LogsAccessPolicy,))
def delete_logs(request):
    return Response({"status": "OK"})


@api_view(["GET"])
@permission_classes((LandingPageAccessPolicy,))
def get_landing_page(request):
    return Response({"status": "OK"})
