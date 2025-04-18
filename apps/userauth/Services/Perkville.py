import secrets
import requests
from django.conf import settings
from requests.exceptions import RequestException

class PerkvilleService:
    @staticmethod
    def get_authorization_url(request):
        """Generate Perkville OAuth URL"""
        config = settings.API_CONFIGS.get('PERKVILLE', {})
        
        # Validate required configuration
        required_keys = [
            'CLIENT_ID', 'CLIENT_SECRET', 'REDIRECT_URI',
            'PERKVILLE_AUTHORIZE_URL', 'PERKVILLE_TOKEN_URL', 'PERKVILLE_SCOPES'
        ]
        for key in required_keys:
            if not config.get(key):
                raise ValueError(f"Missing Perkville config: {key}")

        state = secrets.token_urlsafe(32)
        request.session['perkville_state'] = state
        
        params = {
            'client_id': config['CLIENT_ID'],
            'redirect_uri': config['REDIRECT_URI'],
            'response_type': 'code',
            'scope': config['PERKVILLE_SCOPES'],
            'state': state
        }
        
        return f"{config['PERKVILLE_AUTHORIZE_URL']}?{'&'.join(f'{k}={v}' for k,v in params.items())}", state

    @staticmethod
    def exchange_code_for_token(code, state, request):
        """Exchange authorization code for token"""
        config = settings.API_CONFIGS.get('PERKVILLE', {})
        
        if state != request.session.get('perkville_state'):
            raise ValueError("Invalid state parameter")

        try:
            response = requests.post(
                config['PERKVILLE_TOKEN_URL'],
                data={
                    'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': config['REDIRECT_URI'],
                    'client_id': config['CLIENT_ID'],
                    'client_secret': config['CLIENT_SECRET']
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()['access_token']
        except RequestException as e:
            error = f"Perkville token exchange failed: {str(e)}"
            if e.response:
                error += f" | Status: {e.response.status_code} | Response: {e.response.text[:200]}"
            raise Exception(error)