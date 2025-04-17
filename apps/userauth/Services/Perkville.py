# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import AllowAny
# from rest_framework.response import Response
# import requests
# from django.conf import settings

# @api_view(['GET'])
# @permission_classes([AllowAny])
# def perkville_callback(request):
#     code = request.GET.get('code')
#     state = request.GET.get('state')

#     if state != request.session.get('perkville_oauth_state'):
#         return Response({'error': 'Invalid OAuth state'}, status=400)

#     data = {
#         'grant_type': 'authorization_code',
#         'code': code,
#         'redirect_uri': settings.PERKVILLE_REDIRECT_URI,
#         'client_id': settings.PERKVILLE_CLIENT_ID,
#     }

#     auth = (settings.PERKVILLE_CLIENT_ID, settings.PERKVILLE_CLIENT_SECRET)
#     res = requests.post(settings.PERKVILLE_TOKEN_URL, data=data, auth=auth)

#     if res.status_code != 200:
#         return Response({'error': 'Failed to exchange code for token'}, status=500)

#     access_token = res.json().get('access_token')

#     return Response({'message': 'Perkville Connected', 'token': access_token})




import requests
import logging
import base64
import urllib.parse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework import serializers
from django.shortcuts import redirect

# Set up logger
logger = logging.getLogger(__name__)

# Configuration class for Perkville API
class PerkvilleConfig:
    def __init__(self):
        # Get settings from Django config
        self.client_id = settings.API_CONFIGS['PERKVILLE']['CLIENT_ID']
        self.client_secret = settings.API_CONFIGS['PERKVILLE']['CLIENT_SECRET']
        self.redirect_uri = settings.API_CONFIGS['PERKVILLE']['REDIRECT_URI']
        
        # Base URLs
        self.base_url = "https://www.perkville.com/api"
        # Check if custom domain is provided
        if hasattr(settings.API_CONFIGS['PERKVILLE'], 'CUSTOM_DOMAIN'):
            self.base_url = f"https://www.{settings.API_CONFIGS['PERKVILLE']['CUSTOM_DOMAIN']}/api"
        
        # API endpoints
        self.authorize_url = f"{self.base_url}/authorize/"
        self.token_url = f"{self.base_url}/token/"
        
        
# Perkville OAuth client
class PerkvilleOAuth:
    def __init__(self):
        self.config = PerkvilleConfig()
    
    def get_authorization_url(self, state=None, scopes=None):
        """
        Generate the authorization URL for the OAuth flow
        """
        if scopes is None:
            # Default scopes - adjust based on your needs
            scopes = ["PUBLIC", "USER_CUSTOMER_INFO", "USER_REDEEM", "USER_REFERRAL"]
        
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes)
        }
        
        if state:
            params["state"] = state
        
        # Build the authorization URL
        query_string = urllib.parse.urlencode(params)
        return f"{self.config.authorize_url}?{query_string}"
    
    def exchange_code_for_token(self, code, state=None):
        """
        Exchange authorization code for access token
        """
        # Prepare the request data
        data = {
            "client_id": self.config.client_id,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.config.redirect_uri
        }
        
        if state:
            data["state"] = state
        
        # Prepare Basic Auth header
        auth = (self.config.client_id, self.config.client_secret)
        
        try:
            # Make the token request
            response = requests.post(
                self.config.token_url,
                data=data,
                auth=auth
            )
            
            logger.info(f"Token exchange response: {response.status_code}")
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                logger.error(f"Token exchange failed: {response.text}")
                return {
                    "success": False,
                    "error": "Token exchange failed",
                    "status_code": response.status_code,
                    "message": response.text
                }
        except Exception as e:
            logger.error(f"Exception during token exchange: {str(e)}")
            return {
                "success": False,
                "error": "Request failed",
                "message": str(e)
            }
    
    def password_grant(self, username, password):
        """
        Get token using Resource Owner Password Credentials Grant
        Note: Use this only for administrative purposes
        """
        # Prepare the request data
        data = {
            "grant_type": "password",
            "username": username,
            "password": password,
            "client_id": self.config.client_id
        }
        
        # Prepare Basic Auth header
        auth = (self.config.client_id, self.config.client_secret)
        
        try:
            # Make the token request
            response = requests.post(
                self.config.token_url,
                data=data,
                auth=auth
            )
            
            logger.info(f"Password grant response: {response.status_code}")
            
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                logger.error(f"Password grant failed: {response.text}")
                return {
                    "success": False,
                    "error": "Password grant failed",
                    "status_code": response.status_code,
                    "message": response.text
                }
        except Exception as e:
            logger.error(f"Exception during password grant: {str(e)}")
            return {
                "success": False,
                "error": "Request failed",
                "message": str(e)
            }

# Perkville API client for making authenticated requests
class PerkvilleAPI:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://api.perkville.com/v2"
    
    def make_request(self, endpoint, method="GET", params=None, data=None):
        """
        Make an authenticated request to the Perkville API
        """
        url = f"{self.base_url}/{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                return {"success": False, "error": "Invalid HTTP method"}
            
            if response.status_code in [200, 201, 202, 204]:
                try:
                    if response.text:
                        return {"success": True, "data": response.json()}
                    else:
                        return {"success": True, "data": {"message": "Operation successful"}}
                except ValueError:
                    return {
                        "success": True,
                        "data": {"message": "Operation successful"}
                    }
            else:
                return {
                    "success": False,
                    "error": f"API Error (Status {response.status_code})",
                    "status_code": response.status_code,
                    "message": response.text
                }
        except Exception as e:
            logger.error(f"Exception during API request: {str(e)}")
            return {
                "success": False,
                "error": "Request Failed",
                "message": str(e)
            }