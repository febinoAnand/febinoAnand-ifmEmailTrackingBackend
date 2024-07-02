from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase
from django.urls import reverse, resolve
from settings.views import SettingViewSet
from pushnotification.views import SendReportViewSet

class TestSendSMSView(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_send_sms(self):
        url = reverse('sendsms')
        data = {'message': 'Test message', 'recipient': '+919885674321'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class TestUrls(TestCase):
    def test_sendreport_list_url_resolves(self):
        url = reverse('sendreport-list')  
        self.assertEqual(resolve(url).func.cls, SendReportViewSet)

    def test_setting_list_url_resolves(self):
        url = reverse('setting-list')  
        self.assertEqual(resolve(url).func.cls, SettingViewSet)
