from django.test import TestCase
from django.contrib.auth.models import User, Group
from pushnotification.models import SendReport, NotificationAuth, Setting
from datetime import date, time

class NotificationAuthTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.noti_token = 'sampletoken12345'
        self.notification_auth = NotificationAuth.objects.create(user_to_auth=self.user, noti_token=self.noti_token)

    def test_notification_auth_creation(self):
        self.assertEqual(self.notification_auth.noti_token, self.noti_token)
        self.assertEqual(str(self.notification_auth), f"Notification token for {self.user.username}")

class SendReportTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.group = Group.objects.create(name='testgroup')
        self.notification_auth = NotificationAuth.objects.create(user_to_auth=self.user, noti_token='sampletoken12345')
        self.send_report = SendReport.objects.create(
            date=date.today(),
            time=time(12, 0),
            title='Test Title',
            message='This is a test message',
            send_to_user=self.user,
            users_group=self.group,
        )

    def test_send_report_creation(self):
        self.assertEqual(self.send_report.title, 'Test Title')
        self.assertEqual(self.send_report.message, 'This is a test message')
        self.assertEqual(self.send_report.send_to_user, self.user)
        self.assertEqual(self.send_report.users_group, self.group)
    
    def test_send_report_save(self):
        self.send_report.save()
        self.assertIn(self.send_report.delivery_status, ['200 - OK', 'UserDetail not found', 'Error: '])

class SettingTestCase(TestCase):
    def setUp(self):
        self.application_name = 'Test App'
        self.application_id = 'testapp123'
        self.setting = Setting.objects.create(application_name=self.application_name, application_id=self.application_id)

    def test_setting_creation(self):
        self.assertEqual(self.setting.application_name, self.application_name)
        self.assertEqual(self.setting.application_id, self.application_id)

    def test_single_setting_instance(self):
        with self.assertRaises(ValueError):
            Setting.objects.create(application_name='Another App', application_id='anotherapp123')
