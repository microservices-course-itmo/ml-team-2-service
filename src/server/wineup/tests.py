import json

from django.test import TestCase, Client
from rest_framework import status


class Test(TestCase):
    def test_get_recommendations(self):
        c = Client()
        post_json = "[{\"internal_id\": \"1\"}]"
        c.post('http://localhost:80/users/', json.dumps(post_json), content_type="application/json")
        post_json = "[{\"internal_id\": \"1\", \"all_names\": \"Вино столовое полусладкое розовое ООО «Атанель» «Крымское»\"}, {\"internal_id\": \"2\", \"all_names\": \"Вино Fanagoria Столовое десертное красное ICE WINE (ледяное вино) Saperavi\"}]"
        c.post('http://localhost:80/wines/', json.dumps(post_json), content_type="application/json")
        response = c.get('http://localhost:80/recommendations/1/?page=0&size=20', HTTP_ACCEPT='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(json.loads(response.content)["content"])
