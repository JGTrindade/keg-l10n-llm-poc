import requests
import base64
import lokalise
from classes.tms import *


class LokaliseTMS(TMS):
    def __init__(self, token):
        super().__init__(token)

    def client(self) -> object:
        return lokalise.Client(self.token)

    def upload_file(self, project_id: str, file: str, lang_iso: str) -> str:
        url = f"https://api.lokalise.com/api2/projects/{project_id}/files/upload"

        payload = {
            "lang_iso": lang_iso,
            "filename": file,
            "data": LokaliseTMS.encode_file_to_base64(file)
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)
        return response.text

    @staticmethod
    def encode_file_to_base64(file: str) -> str:
        with open(file, 'rb') as file:
            encoded_string = base64.b64encode(file.read())
            return encoded_string.decode('utf-8')
