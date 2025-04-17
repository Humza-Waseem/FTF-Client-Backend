#  INBODY API INTEGRATION  
import requests
import logging
import os
from django.conf import settings
import requests
import json
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)
class MindbodyAPI:
    # BASE_URL = "https://api.mindbodyonline.com"
    # config = settings.API_CONFIGS['MINDBODY']
    def __init__(self):
        # Updated base URL based on Mindbody API documentation
        self.base_url = "https://api.mindbodyonline.com/public/v6"
        self.api_key = settings.API_CONFIGS['MINDBODY']['API_KEY']
        self.site_id = settings.API_CONFIGS['MINDBODY']['SITE_ID']
        self.user_name = settings.API_CONFIGS['MINDBODY'].get('USER_NAME', '')
        self.password = settings.API_CONFIGS['MINDBODY'].get('PASSWORD', '')
        self.config = settings.API_CONFIGS['MINDBODY']

    
    def create_mindbody_client(self, data):
        url = "https://api.mindbodyonline.com/public/v6/client/addclient"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "API-Key": self.config['API_KEY'],
            "SiteId": self.config['SITE_ID']
        }
        
        payload = {
            "FirstName": data.get("first_name"),
            "LastName": data.get("last_name"),
            "Email": data.get("email"),
            "AddressLine1": data.get("AddressLine1", "N/A"),
            "City": data.get("City", "N/A"),
            "State": data.get("State", "N/A"),
            "PostalCode": data.get("PostalCode", "00000"),
            "BirthDate": data.get("DateOfBirth").strftime("%Y-%m-%d") if data.get("DateOfBirth") else None,
            "MobilePhone": data.get("phone_number", "0000000000"),
            "ReferredBy": data.get("referred_by", "N/A"),
            "Gender": data.get("Gender", "NotProvided"),
            "Password": data.get("password")
        }
        
        print(json.dumps(payload, indent=2))
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            
            print(f"Mindbody API response (status {response.status_code}): {response.text}")
            
            response_data = response.json()
            
            if response.status_code in [200, 201, 202]:
                return response_data
            else:
                return {
                    "error": "API Error",
                    "status_code": response.status_code,
                    "message": response.text
                }
                
        except Exception as e:
            logger.error(f"Exception during Mindbody API call: {str(e)}")
            return {
                "error": "Request Failed",
                "message": f"API request failed: {str(e)}"
            }
            
            
    
    
    
    def send_password_reset_email(self, email, first_name, last_name):
        
        url = "https://api.mindbodyonline.com/public/v6/client/sendpasswordresetemail"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "API-Key": self.config['API_KEY'],
            "SiteId": self.config['SITE_ID']
        }
        
        payload = {
            "UserEmail": email,
            "UserFirstName": first_name,
            "UserLastName": last_name
            # "UserFirstName": data.get("first_name"),
            # "UserLastName": data.get("last_name"),
            # "UserEmail": data.get("email"),
        }
        
        try:
            # Make the API request
            response = requests.post(url, headers=headers, json=payload)
            
            # Log the response
            logger.info(f"Mindbody API response (status {response.status_code}): {response.text}")
            
            # Process the response
            if response.status_code in [200, 201, 202]:
                try:
                    return {"success": True, "data": response.json()}
                except ValueError:
                    return {
                        "success": False,
                        "error": "Invalid JSON response",
                        "status_code": response.status_code,
                        "message": response.text
                    }
            else:
                return {
                    "success": False,
                    "error": f"API Error (Status {response.status_code})",
                    "status_code": response.status_code,
                    "message": response.text
                }
                
        except Exception as e:
            logger.error(f"Exception during Mindbody API call: {str(e)}")
            return {
                "success": False,
                "error": "Request Failed",
                "message": f"API request failed: {str(e)}"
            }