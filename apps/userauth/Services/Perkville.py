import secrets
import logging
from django.conf import settings
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site

logger = logging.getLogger(__name__)

class PerkvilleAPI:
    """Service for handling Perkville API integration"""
    
    @staticmethod
    def generate_authorization_url(request=None, user_id=None):
        """Generate a Perkville authorization URL for a user"""
        try:
            # Generate a random state parameter to prevent CSRF
            state = secrets.token_urlsafe(16)
            
            # Store state in session if request is provided
            if request and hasattr(request, 'session'):
                request.session[f'perkville_state_{user_id}'] = state
            
            # Use the full redirect URI
            redirect_uri = settings.PERKVILLE_REDIRECT_URI
            
            # Construct the authorization URL
            auth_params = {
                'client_id': settings.PERKVILLE_CLIENT_ID,
                'redirect_uri': redirect_uri,
                'response_type': 'code',
                'scope': 'PUBLIC USER_CUSTOMER_INFO',  # Add more scopes as needed
                'state': f"{state}_{user_id}" if user_id else state
            }
            
            auth_url = f"{settings.PERKVILLE_AUTH_URL}?"
            auth_url += "&".join([f"{key}={value}" for key, value in auth_params.items()])
            
            return auth_url
        except Exception as e:
            logger.error(f"Error generating Perkville authorization URL: {str(e)}")
            return None