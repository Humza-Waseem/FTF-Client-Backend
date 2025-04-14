#  INBODY API INTEGRATION  
import requests
import logging
import os
from django.conf import settings
import requests
import json

logger = logging.getLogger(__name__)
   
class InbodyAPI:
    BASE_URL = "https://apiusa.lookinbody.com/"
    
    
    def create_inbody_user(self, data):
        config = settings.API_CONFIGS['INBODY']
        url = f"{self.BASE_URL}User/InsertUser"
        
        headers = {
            "Content-Type": "application/json",
            "API-KEY": config['API_KEY'],
            "Account": config['ACCOUNT']
        }
        
        # Improved gender handling
        gender_map = {
            'male': 'M',
            'female': 'F',
            'm': 'M',
            'f': 'F'
        }
        gender_input = str(data.get("Gender", "")).lower()
        gender_value = gender_map.get(gender_input, 'U')
        
        payload = {           
            "name": data.get("first_name"),
            "iD": data.get("phone_number"),  # Using phone as ID
            "phone": data.get("phone_number"),
            "gender": gender_value,
            "age": data.get("Age"),
            "height": data.get("Height"),
            "weight": data.get("Weight"),
            "birthDay": data.get("DateOfBirth").strftime("%Y-%m-%d") if data.get("DateOfBirth") else None,
            "email": data.get("email"),
        }
        
        try: 
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()  # Raises exception for 4XX/5XX responses
            return response.json()
            
        except Exception as e:
            logger.error(f"Inbody API error: {str(e)}")
            return None