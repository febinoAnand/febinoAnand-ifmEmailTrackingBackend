from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

class TestRouters(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_inbox_router(self):
        url = reverse('inbox-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ticket_router(self):
        url = reverse('ticket-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_email_ids_router(self):
        url = reverse('email_ids-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reports_router(self):
        url = reverse('reports-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_departments_router(self):
        url = reverse('departments-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_settings_router(self):
        url = reverse('emailsettings-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_dashboard_statistics_url(self):
        url = reverse('dashboard_statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)   