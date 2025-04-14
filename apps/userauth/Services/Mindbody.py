#  INBODY API INTEGRATION  
import requests
import logging
import os
from django.conf import settings
import requests
import json

logger = logging.getLogger(__name__)
class MindbodyAPI:
    BASE_URL = "https://api.mindbodyonline.com"
    
    def create_mindbody_client(self, data):
        config = settings.API_CONFIGS['MINDBODY']
        url = "https://api.mindbodyonline.com/public/v6/client/addclient"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "API-Key": config['API_KEY'],
            "SiteId": config['SITE_ID']
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