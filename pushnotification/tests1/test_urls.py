from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from pushnotification.models import SendReport, NotificationAuth, Setting
from django.contrib.auth.models import User, Group

class SendReportViewSetTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Create test data if needed
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.group = Group.objects.create(name='Test Group')
        self.setting = Setting.objects.create(application_name='Test App', application_id='12345')

        self.notificationauth = NotificationAuth.objects.create(user_to_auth=self.user, noti_token='token123')
        self.sendreport = SendReport.objects.create(
            date='2023-01-01',
            time='12:00:00',
            title='Test Report',
            message='This is a test message',
            send_to_user=self.user,
            users_group=self.group,
            delivery_status='-'
        )

    def test_sendreport_list_url(self):
        response = self.client.get(reverse('sendreport-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_notificationauth_detail_url(self):
        detail_url = reverse('notificationauth-detail', args=[self.notificationauth.pk])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_setting_list_url(self):
        response = self.client.get(reverse('setting-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
