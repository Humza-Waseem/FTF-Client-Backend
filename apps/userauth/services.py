import requests
import logging
import os
from django.conf import settings
import requests
import json

logger = logging.getLogger(__name__)

# def create_mindbody_user(user_data):
#     url = "https://api.mindbodyonline.com/public/v6/usertoken/issue"
#     headers = {
#         "Content-Type": "application/json",
#         "API-Key": os.getenv("MINDBODY_API_KEY"),
#         "SiteId": os.getenv("MINDBODY_SITE_ID"), 
#     }
#     try:
#         print(f"Calling Mindbody API with: {user_data}")  
#         response = requests.post(url, headers=headers, json=user_data)
#         print(f"Mindbody Response: {response.status_code} | {response.text}") 
#         response.raise_for_status()
#         return response.json()
#     except Exception as e:
#         print(f"Mindbody Error: {e}")  
#         return None
    
    
    
    
    
    
    
    
#######################################   NEW IMPLEMENTATION  ##########################################


# class MindbodyAPI:
#     BASE_URL = "https://api.mindbodyonline.com"

#     def create_mindbody_client(self, data):
#         url = "https://api.mindbodyonline.com/public/v6/client/addclient"
    
#         headers = {
#           "Accept": "application/json",
#           "Content-Type": "application/json",
#           "API-Key": "cbb223508d584054b360f2b4e7c07b3e",
#           "SiteId": "239323"
#         }
    
#     # Corrected field name mapping
#         payload = {
#           "FirstName": data.get("first_name"),
#             "LastName": data.get("last_name"),
#               "Email": data.get("email"),
#              "AddressLine1": data.get("AddressLine1", "N/A"),  # Corrected
#             "City": data.get("City", "N/A"),  # Corrected
#             "State": data.get("State", "N/A"),  # Corrected
#            "PostalCode": data.get("PostalCode", "00000"),  # Corrected
#            "BirthDate": data.get("DateOfBirth").strftime("%Y-%m-%d") if data.get("DateOfBirth") else None,
#            "MobilePhone": data.get("phone_number", "0000000000"),
#            "ReferredBy": data.get("referred_by", "N/A"),
#            "Gender": data.get("Gender", "NotProvided"),  # Corrected
#            "Password": data.get("password")
#          }
    
#         print(json.dumps(payload, indent=2))
    
#         try:
#            response = requests.post(url, headers=headers, json=payload)
#            response_data = response.json()
        
#         # Improved logging
#            print(f"Mindbody API response (status {response.status_code}): {response.text}")
        
#            if response.status_code in [200, 201, 202]:  # Accept various success codes
#               return response_data
#            else:
#               return {
#                   "Status": "Failure",
#                   "status_code": response.status_code,
#                   "message": response.text
#                 }
#         except Exception as e:
#             print(f"Exception during Mindbody API call: {str(e)}")
#             return {
#             "Status": "Failure",
#             "message": f"API request failed: {str(e)}"
#         }



    # def validate_login(self, email, password):
    #     url = f'{self.BASE_URL}client/validate'
    #     payload = {"Username": email, "Password": password}
    #     headers = {'Content-Type': 'application/json'}
    #     response = requests.post(url, json=payload, headers=headers)
    #     return response.json()

    # def reset_password(self, email):
    #     url = f'{self.BASE_URL}client/passwordreset'
    #     payload = {"Email": email}
    #     headers = {'Content-Type': 'application/json'}
    #     response = requests.post(url, json=payload, headers=headers)
    #     return response.json()
    
    
    
    
    
    
    
    
    
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
    
    
    
    
    
    
    
    
#?#############################  INBODY API INTEGRATION  ################################    
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