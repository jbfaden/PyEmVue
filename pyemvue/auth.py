from datetime import datetime
from typing import Optional, Callable, Dict
from jose import jwt
import requests
import datetime

# These provide AWS cognito authentication support
import boto3
import botocore
from pycognito import Cognito
import requests

CLIENT_ID = '4qte47jbstod8apnfic0bunmrq'
USER_POOL = 'us-east-2_ghlOXVLi1'

class Auth:
    def __init__(
        self,
        host: str,
        username: str = None,
        password: str = None,
        tokens: Optional[Dict[str, str]] = None,
        token_updater: Optional[Callable[[Dict[str, str]], None]] = None,
    ):
        self.host = host
        self.token_updater = token_updater
        # Use pycognito to go through the SRP authentication to get an auth token and refresh token
        self.client = boto3.client(
            'cognito-idp', 
            region_name='us-east-2', 
            config=botocore.client.Config(signature_version=botocore.UNSIGNED)
        )

        if tokens and tokens['access_token'] and tokens['id_token'] and tokens['refresh_token']:
            # use existing tokens
            self.cognito = Cognito(USER_POOL, CLIENT_ID,
                user_pool_region='us-east-2', 
                id_token=tokens['id_token'], 
                access_token=tokens['access_token'], 
                refresh_token=tokens['refresh_token'])
        elif username and password:
            #log in with username and password
            self.cognito = Cognito(USER_POOL, CLIENT_ID, 
                user_pool_region='us-east-2', username=username)
            self.cognito.authenticate(password=password)

        self.tokens = self.refresh_tokens()

    def refresh_tokens(self) -> Dict[str, str]:
        """Refresh and return new tokens."""
        self.cognito.renew_access_token()
        tokens = self._extract_tokens_from_cognito()

        if self.token_updater is not None:
            self.token_updater(tokens)

        return tokens

    def get_username(self) -> str:
        """Get the username associated with the logged in user."""
        user = self.cognito.get_user()
        return user._data['email']

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        """Make a request."""
        headers = kwargs.get("headers")

        if headers is None:
            headers = {}
        else:
            headers = dict(headers)

        #pycognito's method for checking expiry, but without the hard dependency on the cognito object
        now = datetime.datetime.now()
        dec_access_token = jwt.get_unverified_claims(self.tokens['access_token'])

        if now > datetime.datetime.fromtimestamp(dec_access_token["exp"]):
            # expired
            self.tokens = self.refresh_tokens()

        headers["authtoken"] = self.tokens['id_token']

        return requests.request(
            method, f"{self.host}/{path}", **kwargs, headers=headers,
        )

    def _extract_tokens_from_cognito(self) -> Dict[str, str]:
        return {
            'access_token': self.cognito.access_token,
            'id_token': self.cognito.id_token, # Emporia uses this token for authentication
            'refresh_token': self.cognito.refresh_token,
            'token_type': self.cognito.token_type
        }
