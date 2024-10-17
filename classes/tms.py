from abc import ABC, abstractmethod


class TMS(ABC):
    def __init__(self, token: str):
        self.token = token
        self.client = self.client()

    @abstractmethod
    def client(self) -> object:
        pass

    @abstractmethod
    def upload_file(self, project_id: str, file: str, lang_iso: str) -> object:
        pass
