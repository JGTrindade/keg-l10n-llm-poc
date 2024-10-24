import requests


class APIClient:
    def __init__(self, base_url: str, headers: dict = None):
        self.base_url = base_url
        self.headers = headers

    def get(self, path: str = None, params: dict = None):
        url = f"{self.base_url}/{path if path else ''}"
        response = requests.get(url, params, headers=self.headers)
        if response.ok:
            return response.json()
        else:
            print(f"An error occurred while sending the request")

    def get_institution_id(self, institution_id: str):
        return self.get(path=f"school/{institution_id}/cards", params={'blocks': 'true'})
