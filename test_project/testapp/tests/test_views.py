from django.contrib.auth.models import Group, User
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from test_project.testapp.models import UserAccount


class LogsTestCase(APITestCase):
    def setUp(self):
        UserAccount.objects.all().delete()
        User.objects.all().delete()
        Group.objects.all().delete()

    def test_admin_can_do_anything_with_logs(self):
        admin_group = Group.objects.create(name="admin")
        admin_user = User.objects.create()
        admin_user.groups.add(admin_group)
        self.client.force_authenticate(user=admin_user)

        url = reverse("get-logs")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

        url = reverse("delete-logs")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, 200)

    def test_dev_can_only_get_logs(self):
        dev_group = Group.objects.create(name="dev")
        dev_user = User.objects.create()
        dev_user.groups.add(dev_group)
        self.client.force_authenticate(user=dev_user)

        url = reverse("get-logs")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

        url = reverse("delete-logs")
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, 403)
