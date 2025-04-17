import requests
from django.conf import settings

def get_nutrition(query):
    response = requests.post(
        f"{settings.NUTRITIONIX_CONFIG['BASE_URL']}/natural/nutrients",
        headers={
            "x-app-id": settings.NUTRITIONIX_CONFIG['APP_ID'],
            "x-app-key": settings.NUTRITIONIX_CONFIG['APP_KEY'],
            "Content-Type": "application/json"
        },
        json={"query": query}
    )
    response.raise_for_status()  
    return response.json()

print(get_nutrition("1 cup oatmeal and 1 banana"))