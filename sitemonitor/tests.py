from unittest import mock
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Site, SiteStatusHistory
from .tasks import monitor_sites

User = get_user_model()


class SiteAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='Password123!')
        resp = self.client.post(reverse('register'), {
            'username': 'tester2', 'password': 'Password123!'
        })
        # Register returns token directly

    def authenticate(self):
        login_resp = self.client.post('/api/auth/login/', {'username': 'tester', 'password': 'Password123!'}, format='json')
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)
        token = login_resp.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

    def test_create_site(self):
        self.authenticate()
        resp = self.client.post('/api/sites/', {
            'name': 'Example', 'url': 'https://example.com', 'client_name': 'Client', 'site_type': 'website'
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Site.objects.count(), 1)

    @mock.patch('sitemonitor.tasks.requests.get')
    def test_monitor_task_records_history(self, mock_get):
        self.authenticate()
        site = Site.objects.create(owner=self.user, name='Example', url='https://example.com', client_name='C', site_type='website')
        mock_get.return_value.status_code = 200
        monitor_sites()  # run task directly
        self.assertEqual(site.history.count(), 1)
        h = site.history.first()
        self.assertEqual(h.status, 'up')

