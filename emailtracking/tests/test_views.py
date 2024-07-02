from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.utils import timezone
from django.contrib.auth import get_user_model
from ..models import Inbox, Ticket, EmailID, Report, Department, Setting
from ..serializers import InboxSerializer, ReportSerializer, DepartmentSerializer, SettingSerializer
from rest_framework.response import Response 

class InboxViewSetTestCase(APITestCase):

    def setUp(self):
        self.inbox1 = Inbox.objects.create(
            date='2024-07-01', 
            time='12:00:00',
            from_email='sender@example.com',
            to_email='receiver@example.com',
            subject='Test Subject 1',
            message='Test Message 1',
            message_id=1
        )
        self.inbox2 = Inbox.objects.create(
            date='2024-07-02', 
            time='13:00:00',
            from_email='sender2@example.com',
            to_email='receiver2@example.com',
            subject='Test Subject 2',
            message='Test Message 2',
            message_id=2
        )

        self.url = reverse('inbox-list')

    def test_get_inbox_list(self):
        response = self.client.get(self.url)
        inboxes = Inbox.objects.all()
        serializer = InboxSerializer(inboxes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_delete_inbox(self):
        url = reverse('inbox-detail', args=[self.inbox1.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Inbox.objects.filter(id=self.inbox1.pk).exists())

class TicketViewSetTestCase(APITestCase):
    def setUp(self):
        self.inbox = Inbox.objects.create(
            date=timezone.now().date(),
            time=timezone.now().time(),
            from_email='from@example.com',
            to_email='to@example.com',
            subject='Test Subject',
            message='Test message content',
            message_id=1
        )
        self.ticket = Ticket.objects.create(
            ticketname='Test Ticket',
            inboxMessage=self.inbox,
            actual_json={"key": "value"},
            is_satisfied=False
        )
        self.ticket_url = reverse('ticket-detail', args=[self.ticket.pk])
        self.tickets_url = reverse('ticket-list')

    def test_get_ticket(self):
        response = self.client.get(self.ticket_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ticketname'], 'Test Ticket')

    def test_get_all_tickets(self):
        response = self.client.get(self.tickets_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_delete_ticket(self):
        response = self.client.delete(self.ticket_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ticket.objects.filter(id=self.ticket.pk).exists())

class EmailIDViewSetTestCase(APITestCase):

    def setUp(self):
        self.email_id_1 = EmailID.objects.create(email='test1@example.com')
        self.email_id_2 = EmailID.objects.create(email='test2@example.com')

        self.valid_payload = {
            'email': 'test3@example.com',
            'active': True
        }
        self.invalid_payload = {
            'email': '',
            'active': True
        }

        self.update_payload = {
            'email': 'updated@example.com',
            'active': False
        }

    def test_create_email_id(self):
        response = self.client.post(reverse('email_ids-list'), data=self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EmailID.objects.count(), 3)
        self.assertEqual(EmailID.objects.get(id=response.data['id']).email, 'test3@example.com')

    def test_create_invalid_email_id(self):
        response = self.client.post(reverse('email_ids-list'), data=self.invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_email_id(self):
        response = self.client.get(reverse('email_ids-detail', kwargs={'pk': self.email_id_1.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.email_id_1.email)

    def test_update_email_id(self):
        response = self.client.put(reverse('email_ids-detail', kwargs={'pk': self.email_id_1.pk}), data=self.update_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.email_id_1.refresh_from_db()
        self.assertEqual(self.email_id_1.email, 'updated@example.com')
        self.assertEqual(self.email_id_1.active, False)

    def test_delete_email_id(self):
        response = self.client.delete(reverse('email_ids-detail', kwargs={'pk': self.email_id_1.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(EmailID.objects.count(), 1)

    def test_list_email_ids(self):
        response = self.client.get(reverse('email_ids-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

class ReportViewSetTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.report1 = Report.objects.create(Department="Department 1", message="Message 1")
        self.report2 = Report.objects.create(Department="Department 2", message="Message 2")

    def test_get_reports(self):
        url = reverse('reports-list')
        response = self.client.get(url)
        reports = Report.objects.all()
        serializer = ReportSerializer(reports, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_delete_report(self):
        url = reverse('reports-detail', args=[self.report1.pk])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Report.objects.filter(id=self.report1.pk).exists())

class DepartmentViewSetTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.department1 = Department.objects.create(dep_alias="Alias1", department="Department 1")
        self.department2 = Department.objects.create(dep_alias="Alias2", department="Department 2")

    def test_get_departments(self):
        url = reverse('departments-list')
        response = self.client.get(url)
        departments = Department.objects.all()
        serializer = DepartmentSerializer(departments, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_update_department(self):
        url = reverse('departments-detail', args=[self.department1.id])
        updated_data = {'dep_alias': 'Updated Alias', 'department': 'Updated Department'}

        response = self.client.patch(url, updated_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.department1.refresh_from_db()
        self.assertEqual(self.department1.dep_alias, 'Updated Alias')
        self.assertEqual(self.department1.department, 'Updated Department')

class SettingViewSetTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.settings_url = reverse('emailsettings-list')  

        # Create a sample Setting instance
        self.setting_data = {
            'host': 'test_host',
            'port': 8081,
            'username': 'test_user',
            'password': 'test_password',
            'checkstatus': True,
            'checkinterval': 30
        }
        self.setting = Setting.objects.create(**self.setting_data)

    def test_list_settings(self):
        response = self.client.get(self.settings_url)
        settings = Setting.objects.all()
        serializer = SettingSerializer(settings, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_setting_unique_constraint(self):
        second_setting_data = {
            'host': 'another_host',
            'port': 8082,
            'username': 'another_user',
            'password': 'another_password',
            'checkstatus': False,
            'checkinterval': 45
        }
        try:
            response = self.client.post(self.settings_url, second_setting_data, format='json')
        except ValueError as e:
            self.assertEqual(str(e), "Only one instance of Settings can be created")

        # Verify that no additional Setting instance was created
        self.assertEqual(Setting.objects.count(), 1)

    def test_update_setting(self):
        update_data = {
            'port': 9090,
            'checkinterval': 60
        }
        detail_url = reverse('emailsettings-detail', args=[self.setting.pk])
        response = self.client.put(detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.setting.refresh_from_db()
        self.assertEqual(self.setting.port, update_data['port'])
        self.assertEqual(self.setting.checkinterval, update_data['checkinterval'])

    def test_delete_setting(self):
        detail_url = reverse('emailsettings-detail', args=[self.setting.pk])
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Setting.objects.filter(pk=self.setting.pk).exists())

from django.utils import timezone
from collections import OrderedDict


class DashboardStatisticsTestCase(APITestCase):
    def setUp(self):
        User = get_user_model()
        # Create some users
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='password1', is_active=True)
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='password2', is_active=False)

        # Create some departments
        self.department1 = Department.objects.create(dep_alias='Dep1', department='Dep1')
        self.department2 = Department.objects.create(dep_alias='Dep2', department='Dep2')

        # Add users to departments
        self.department1.users_to_send.add(self.user1)
        self.department2.users_to_send.add(self.user2)

        # Create some inbox messages
        self.inbox1 = Inbox.objects.create(date=timezone.now().date(), time=timezone.now().time(), from_email='a@example.com', to_email='b@example.com', subject='Subject 1', message='Message 1', message_id=1)
        self.inbox2 = Inbox.objects.create(date=timezone.now().date(), time=timezone.now().time(), from_email='c@example.com', to_email='d@example.com', subject='Subject 2', message='Message 2', message_id=2)

        # Create some tickets
        self.ticket1 = Ticket.objects.create(ticketname='Ticket 1', inboxMessage=self.inbox1, actual_json={}, is_satisfied=False)
        self.ticket2 = Ticket.objects.create(ticketname='Ticket 2', inboxMessage=self.inbox2, actual_json={}, is_satisfied=True)

        # Create some reports
        self.report1 = Report.objects.create(date=timezone.now().date(), time=timezone.now().time(), Department='Dep1', message='Report Message 1')
        self.report2 = Report.objects.create(date=timezone.now().date(), time=timezone.now().time(), Department='Dep2', message='Report Message 2')

        # Create some email IDs
        self.email_id1 = EmailID.objects.create(email='email1@example.com')
        self.email_id2 = EmailID.objects.create(email='email2@example.com')
        
    def test_get_dashboard_statistics(self):
        url = reverse('dashboard_statistics')
        response = self.client.get(url)
        
        print("Response Data: ", response.data)
        
        expected_data = {
            'total_users': 2,
            'active_users': 1,
            'inactive_users': 1,
            'total_departments': 2,
            'total_inbox': 2,
            'total_tickets': 2,
            'department_ticket_count': [
                {'department_id': self.department1.pk, 'department_name': 'Dep1', 'ticket_count': 1},
                {'department_id': self.department2.pk, 'department_name': 'Dep2', 'ticket_count': 1}
            ],
            'user_details': [
                {'id': self.user1.id, 'username': 'user1', 'email': 'user1@example.com', 'is_active': True, 'user_detail': None},
                {'id': self.user2.id, 'username': 'user2', 'email': 'user2@example.com', 'is_active': False, 'user_detail': None}
            ]
        }
        
        print("Expected Data: ", expected_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)