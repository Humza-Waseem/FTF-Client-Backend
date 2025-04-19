import urllib.parse

def get_perkville_authorization_url():
    client_id = 'Hsn0jDeAvCTMuDNBaWOd7o8rsQtHno'
    redirect_uri = 'https://biz/8929/perkville/callback/'
    response_type = 'code'
    scope = 'user'

    base_url = 'https://www.perkville.com/oauth2/authorize/'
    params = {
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': response_type,
        'scope': scope,
    }

    return f"{base_url}?{urllib.parse.urlencode(params)}"
