import api_types
import utils
import requests
from http import HTTPStatus
import json
import time

base_url = "https://graph.threads.net/v1.0"

class ThreadsMeta:
    def __init__(self, access_token: str, secret: str, client_id: str) -> None:
        self.access_token = access_token
        self.secret = secret
        self.client_id = client_id

        print("getting user threads id")

        response = self._get_myself()

        if isinstance(response, api_types.Error):
            json_formatted_str = json.dumps(response.to_json(), indent=2)
            raise ValueError(f"An error occured initializing threads: {json_formatted_str}")

        self.user_id = response.id

    def _get_myself(self) -> api_types.Error | api_types.IDResponse:
        full_url = f"{base_url}/me?fields=id,name&access_token={self.access_token}"

        try:
            resp = requests.get(full_url)
            json_data = json.loads(resp.content)

            if resp.status_code != HTTPStatus.OK:
                return utils.parse_response(json_data, api_types.Error)
            
            return utils.parse_response(json_data, api_types.IDResponse)
        except requests.exceptions.RequestException as err:
            return api_types.Error(error=api_types.ErrorDetail(message=f"Network error: {err}"))
        except Exception as err:
            return api_types.Error(error=api_types.ErrorDetail(message=f"Unexpected error: {err}"))

    def get_long_lived_token(self) -> api_types.TokenResponse | api_types.Error:
        """This is getting a long-lived token using the short-lived token"""

        endpoint = f"/access_token"
        full_url = f"{base_url}{endpoint}?grant_type=th_exchange_token&client_secret={self.secret}&access_token={self.access_token}"
        resp = requests.get(full_url)
        json_data = json.loads(resp.content)

        if resp.status_code != HTTPStatus.OK:
            parsed_err = utils.parse_response(json_data, api_types.Error)
            return parsed_err
        
        return utils.parse_response(json_data, api_types.TokenResponse)

    def refresh_token(self) -> api_types.TokenResponse | None:
        ''' The access token that's supposed to have been initialized needs to be a long lived token '''
        global url 
        full_url = f"/refresh_access_token?grant_type=th_refresh_token&access_token={self.access_token}"

    def _create_thread(self, text: str): 
        """ This endpoint is for creating a media container and it only works for texts"""
        if not text:
            return api_types.Error(error=api_types.ErrorDetail(message="Text cannot be empty"))

        endpoint = f"/{self.user_id}/threads"
        full_url = f"{base_url}{endpoint}?media_type=TEXT&text={text}&access_token={self.access_token}"

        print("creating thread.....")
        try:
            resp = requests.post(full_url)
            json_data = json.loads(resp.content)

            if resp.status_code != HTTPStatus.OK:
                parsed_err = utils.parse_response(json_data, api_types.Error)
                return parsed_err

            return utils.parse_response(json_data, api_types.IDResponse)

        except requests.exceptions.RequestException as err:
            return api_types.Error(error=api_types.ErrorDetail(message=f"Network error: {err}"))
        except Exception as err:
            return api_types.Error(error=api_types.ErrorDetail(message=f"Unexpected error: {err}"))
    
    def publish_thread(self, text: str):
        """ This endpoint only publishes text thread"""
        try:
            creation_resp = self._create_thread(text)
            if isinstance(creation_resp, api_types.Error):
                return creation_resp
            
            endpoint = f"/{self.user_id}/threads_publish"
            full_url = f"{base_url}{endpoint}?creation_id={creation_resp.id}&access_token={self.access_token}"

            print("Thread created successfully, waiting 30s before publishing thread....")
            time.sleep(30)

            resp = requests.post(full_url)
            json_data = json.loads(resp.content)

            if resp.status_code != HTTPStatus.OK:
                parsed_err = utils.parse_response(json_data, api_types.Error)
                return parsed_err

            return utils.parse_response(json_data, api_types.IDResponse)
            
        except requests.exceptions.RequestException as err:
            return api_types.Error(error=api_types.ErrorDetail(message=f"Network error: {err}"))
        except Exception as err:
            return api_types.Error(error=api_types.ErrorDetail(message=f"Unexpected error: {err}"))