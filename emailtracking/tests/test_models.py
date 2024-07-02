from django.test import TestCase
from django.contrib.auth.models import User
from emailtracking.models import Inbox, Ticket, Report, Setting, EmailID, Department

class ModelTestCase(TestCase):

    def setUp(self):
    
        self.user = User.objects.create_user(username='testuser', password='12345')


        self.inbox = Inbox.objects.create(
            date='2023-06-27',
            time='14:00:00',
            from_email='from@example.com',
            to_email='to@example.com',
            subject='Test Subject',
            message='Test message'
        )

    
        self.ticket = Ticket.objects.create(
            ticketname='Test Ticket',
            inboxMessage=self.inbox
        )

    
        self.report = Report.objects.create(
            Department='IT',
            message='Test message'
        )
        self.report.send_to_user.add(self.user)

        
        self.setting = Setting.objects.create(
            host='localhost',
            port=8000,
            username='admin',
            password='admin123'
        )

    
        self.emailid = EmailID.objects.create(
            email='email@example.com'
        )

    
        self.department = Department.objects.create(
            dep_alias='IT',
            department='Information Technology'
        )
        self.department.users_to_send.add(self.user)

    def test_inbox_creation(self):
        inbox = Inbox.objects.get(subject='Test Subject')
        self.assertEqual(inbox.from_email, 'from@example.com')

    def test_ticket_creation(self):
        ticket = Ticket.objects.get(ticketname='Test Ticket')
        self.assertEqual(ticket.inboxMessage, self.inbox)
        self.assertEqual(ticket.is_satisfied, False)

    def test_ticket_auto_date_time(self):
        ticket = Ticket.objects.get(ticketname='Test Ticket')
        self.assertIsNotNone(ticket.date)
        self.assertIsNotNone(ticket.time)

    def test_report_creation(self):
        report = Report.objects.get(Department='IT')
        self.assertEqual(report.message, 'Test message')
        self.assertIn(self.user, report.send_to_user.all())

    def test_setting_creation(self):
        setting = Setting.objects.get(host='localhost')
        self.assertEqual(setting.port, 8000)
        with self.assertRaises(ValueError):
            Setting.objects.create()

    def test_emailid_creation(self):
        emailid = EmailID.objects.get(email='email@example.com')
        self.assertEqual(emailid.active, True)

    def test_department_creation(self):
        department = Department.objects.get(dep_alias='IT')
        self.assertEqual(department.department, 'Information Technology')
        self.assertIn(self.user, department.users_to_send.all())

    def test_department_unique_constraint(self):
        with self.assertRaises(Exception):
            Department.objects.create(dep_alias='IT', department='Information Technology')
