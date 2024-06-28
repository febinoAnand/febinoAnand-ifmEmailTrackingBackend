from django.test import TestCase
from smsgateway.models import SMSNumber, Setting, SendReport
from django.core.exceptions import ValidationError


class SMSNumberTestCase(TestCase):
    def test_smsnumber_creation(self):
        smsnumber = SMSNumber(smsnumber="+919876543210", description="Test number")
        smsnumber.save()
        self.assertEqual(SMSNumber.objects.count(), 1)

    def test_smsnumber_validation(self):
        with self.assertRaises(ValidationError):
            smsnumber = SMSNumber(smsnumber="9876543210", description="Test number")
            smsnumber.full_clean()

class SettingTestCase(TestCase):
    def test_setting_creation(self):
        setting = Setting(sid="test_sid", auth_token="test_auth_token")
        setting.save()
        self.assertEqual(Setting.objects.count(), 1)

    def test_setting_unique_instance(self):
        setting1 = Setting(sid="test_sid", auth_token="test_auth_token")
        setting1.save()
        with self.assertRaises(ValueError):
            setting2 = Setting(sid="test_sid2", auth_token="test_auth_token2")
            setting2.save()

class SendReportTestCase(TestCase):
    def test_sendreport_creation(self):
        smsnumber = SMSNumber(smsnumber="+919876543210", description="Test number")
        smsnumber.save()
        setting = Setting(sid="test_sid", auth_token="test_auth_token")
        setting.save()
        sendreport = SendReport(to_number="+919012345678", from_number=smsnumber, message="Test message")
        sendreport.save()
        self.assertEqual(SendReport.objects.count(), 1)

    def test_sendreport_validation(self):
        smsnumber = SMSNumber(smsnumber="+919876543210", description="Test number")
        smsnumber.save()
        with self.assertRaises(ValidationError):
            sendreport = SendReport(to_number="9012345678", from_number=smsnumber, message="Test message")
            sendreport.full_clean()