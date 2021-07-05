from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from test_project.testapp.access_policies import (
    LogsAccessPolicy,
    UserAccountAccessPolicy,
    LandingPageAccessPolicy
)
from test_project.testapp.models import UserAccount
from test_project.testapp.serializers import UserAccountSerializer


class UserAccountViewSet(viewsets.ModelViewSet):
    permission_classes = (UserAccountAccessPolicy,)
    serializer_class = UserAccountSerializer
    queryset = UserAccount.objects.all()

    @action(detail=True, methods=["post"])
    def set_password(self, request, pk=None):
        return Response({}, status=200)


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
