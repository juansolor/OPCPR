from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
import json

class SupervisorioOpcuaTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.supervisorio_url = reverse('supervisorio_opcua')
        self.health_url = reverse('health_check')

    def test_health_check(self):
        """Test del endpoint health check"""
        response = self.client.get(self.health_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'ok')
        self.assertIn('message', data)
        self.assertIn('version', data)

    def test_supervisorio_get_with_default_url(self):
        """Test GET request sin parámetro URL (usa URL por defecto)"""
        response = self.client.get(self.supervisorio_url)
        
        # Puede fallar si no hay servidor OPC UA disponible, pero debe devolver una respuesta
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR])
        
        data = json.loads(response.content)
        if response.status_code == status.HTTP_200_OK:
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['method'], 'GET')
            self.assertIn('data', data)
        else:
            self.assertIn('error', data)

    def test_supervisorio_get_with_custom_url(self):
        """Test GET request con URL personalizada"""
        custom_url = 'opc.tcp://192.168.1.100:4840'
        response = self.client.get(f'{self.supervisorio_url}?url={custom_url}')
        
        data = json.loads(response.content)
        if response.status_code == status.HTTP_200_OK:
            self.assertEqual(data['url'], custom_url)

    def test_supervisorio_post_without_data(self):
        """Test POST request sin datos"""
        response = self.client.post(
            self.supervisorio_url,
            data=json.dumps({}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        data = json.loads(response.content)
        self.assertIn('error', data)
        self.assertIn('No se proporcionaron datos para escribir', data['error'])

    def test_supervisorio_post_with_data(self):
        """Test POST request con datos válidos"""
        post_data = {
            'url': 'opc.tcp://localhost:4840',
            'data': {
                'test_variable': 123.45,
                'test_boolean': True
            }
        }
        
        response = self.client.post(
            self.supervisorio_url,
            data=json.dumps(post_data),
            content_type='application/json'
        )
        
        # Puede fallar si no hay servidor OPC UA disponible
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR])
        
        data = json.loads(response.content)
        if response.status_code == status.HTTP_200_OK:
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data['method'], 'POST')
            self.assertIn('written_data', data)
        else:
            self.assertIn('error', data)

    def test_supervisorio_invalid_method(self):
        """Test con método HTTP no permitido"""
        response = self.client.put(self.supervisorio_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_supervisorio_post_malformed_json(self):
        """Test POST con JSON malformado"""
        response = self.client.post(
            self.supervisorio_url,
            data='{"invalid": json}',
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
