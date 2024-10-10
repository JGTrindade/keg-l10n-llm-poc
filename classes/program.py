import requests


class Program:
    def __init__(self):
        self.program_list_endpoint = 'https://www.studentshub.com/api/sanity/program-list'

    def get_all_ids(self) -> list:
        r = requests.get(self.program_list_endpoint)
        if r.ok:
            all_program_ids = r.json()
            return all_program_ids

    def get_number_of_programs(self) -> int:
        return len(self.get_all_ids())
