from django.test import TestCase, Client
from rest_framework import status


class Test(TestCase):
    def test_get_recommendations(self):
        c = Client()
        response = c.get('http://localhost:80/recommendations/1/', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.wine_id)
