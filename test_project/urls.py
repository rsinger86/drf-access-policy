from django.conf.urls import url, include
from rest_framework import routers
from test_project.testapp.views import UserAccountViewSet


# Standard viewsets
router = routers.DefaultRouter()
router.register(r"accounts", UserAccountViewSet, base_name="account")

urlpatterns = [url(r"^", include(router.urls))]
