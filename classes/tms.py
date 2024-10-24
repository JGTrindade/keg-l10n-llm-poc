from abc import ABC, abstractmethod


class TMS(ABC):
    def __init__(self, token: str):
        self.token = token
        self.client = None

    def fetch_projects(self, params: dict = None):
        pass

    @abstractmethod
    def upload_file(self, project_id: str, params: dict) -> object:
        pass
