# from django.test import TestCase
# from rest_framework.test import APIClient
# from unittest.mock import patch

# class InBODYUSERTestCase(TestCase):
    
#     @patch('requests.post')
#     def test_create_user_success(self, mock_post):
#         # Mock the API response
#         mock_post.return_value.status_code = 200
#         mock_post.return_value.json.return_value = {"success": True}
        
#         client = APIClient()
#         response = client.post('/your-endpoint/', {}, format='json')
        
#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(response.data['success'])
    
#     @patch('requests.post')
#     def test_create_user_failure(self, mock_post):
#         mock_post.return_value.status_code = 400
#         mock_post.return_value.text = "Bad Request"
        
#         client = APIClient()
#         response = client.post('/your-endpoint/', {}, format='json')
        
#         self.assertEqual(response.status_code, 400)