from django.test import TestCase, Client
from rest_framework import status
from ..models import SendReport, Setting, SMSNumber
from ..serializers import SendReportViewSerializer, SettingViewSerializer

class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.from_sms_number = SMSNumber.objects.create(smsnumber='+9876543210', description='Test From SMS Number')
        self.to_sms_number = SMSNumber.objects.create(smsnumber='+1234567890', description='Test To SMS Number')
        self.setting = Setting.objects.create(sid='Test SID', auth_token='Test Auth Token')
        self.send_report = SendReport.objects.create(to_number=self.to_sms_number, from_number=self.from_sms_number, message='This is a test report')

    def test_send_report_viewset(self):
        response = self.client.get('/sendreport/', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)

    def test_setting_viewset(self):
        response = self.client.get('/setting/', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)

    def test_send_sms_view(self):
        data = {'to_number': self.to_sms_number.id, 'from_number': self.from_sms_number.id, 'message': 'This is a test message'}
        response = self.client.post('/sendsms/', data, format='json', content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'message': 'Message sent'})