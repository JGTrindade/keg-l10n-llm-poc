from typing import TypedDict
from classes.tms import TMS
import lokalise


class FileUploadData(TypedDict):
    data: str
    filename: str
    lang_iso: str


class LokaliseTMS(TMS):
    def __init__(self, token):
        super().__init__(token)
        self.client = lokalise.Client(self.token)

    def fetch_projects(self, params: dict = None):
        return self.client.projects(params)

    def upload_file(self, project_id: str, params: FileUploadData) -> lokalise.client.QueuedProcessModel:
        return self.client.upload_file(project_id, params)
