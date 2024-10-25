from classes.db import DB
from classes.lokalisetms import LokaliseTMS
from classes.APIClient import APIClient
from classes.project import Project
from classes.institution import Institution
from dotenv import load_dotenv
import requests
import json
import os
import base64


class App:
    def __init__(self):
        load_dotenv()
        self.tms = LokaliseTMS(os.getenv('TMS_TOKEN'))
        self.project = Project(self.tms)
        self.api_client = APIClient(base_url=os.getenv('STDHUB_API_BASE_URL'),
                                    headers={"x-api-key": os.getenv('STDHUB_API_AUTH_KEY')})
        self.institution = Institution(self.api_client)
        self.db = DB('keg_l10n_llm_poc')

    @staticmethod
    def clear_console():
        # Check the platform and run the appropriate clear command
        if os.name == 'nt':  # For Windows
            os.system('cls')
        else:  # For macOS and Linux
            os.system('clear')

    @staticmethod
    def display_welcome_message():
        print('*** KEG L10N LLM POC ***\n')

    @staticmethod
    def prompt_user(message: str) -> str:
        return input(message)

    def handle_choice(self, choice: str):
        if choice == '1':
            num_of_institutions_to_send_to_tms = int(
                input("Insert the number of institutions to send content for review (max 500).\n"))
            return self.fetch_institutions_never_sent_to_tms(num_of_institutions_to_send_to_tms)
        # else:
        #     num_of_institutions_to_send_to_tms = int(
        #         input("Insert the number of programs to send content for review (max 500).\n"))
        #     return self.handle_programs(num_of_institutions_to_send_to_tms)

    def fetch_institutions_never_sent_to_tms(self, num_of_institutions_to_send_to_tms: int) -> tuple:
        institutions_in_db = self.db.query("SELECT id FROM institutions").fetchall()
        latest_institutions = self.institution.fetch_all_ids_from_external_db()

        data = list()
        for institution in latest_institutions:
            if all(institution != institution_in_db[0] for institution_in_db in institutions_in_db):
                data.append(tuple((institution, 0)))

        if data:
            # Insert data with INSERT OR IGNORE to avoid duplicate ID errors
            self.db.query("INSERT OR IGNORE INTO institutions (id, sent_to_tms) VALUES (?, ?);", data)
            self.db.commit()

        institutions_never_sent_to_tms = (self.db.query("SELECT * FROM institutions WHERE sent_to_tms = 0 LIMIT ?",
                                                        (num_of_institutions_to_send_to_tms,)).fetchall())

        return institutions_never_sent_to_tms

    # def handle_programs(self, num_of_programs_to_send_to_tms: int) -> None:
    #     for program_id in num_of_programs_to_send_to_tms:
    #         url = f'{base_url}/program/{program_id}/cards?blocks=1'
    #         r = requests.get(url)
    #         if r.ok:
    #             data = r.json()
    #             blocks = data[0]['item']['blocks']
    #             # Filter blocks that are not pure markup
    #             blocks_of_pure_text = {}
    #             for index, block in enumerate(blocks):
    #                 if len(block) > 1 and block[0] != "<" and block[-1] != ">":
    #                     blocks_of_pure_text[f'key{index}'] = block
    #                     # Adjust the counter of used keys for LLM reviews
    #                     # keys_from_llm_projects = keys_from_llm_projects + len(blocks_of_pure_text)
    #                     print(blocks_of_pure_text)
    #         else:
    #             print('Something went wrong.')

    @staticmethod
    def save_dict_as_json(data: dict, file_path: str) -> None:
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)
        except IOError as e:
            print(f"An error occurred while saving the file: {e}")

    @staticmethod
    def encode_file_to_base64(file: bytes) -> str:
        with open(file, 'rb') as file:
            encoded_string = base64.b64encode(file.read())
            return encoded_string.decode('utf-8')

    @staticmethod
    def list_files_in_directory(directory: str) -> list:
        files = []

        for roots, dirs, files in os.walk(directory):
            files_in_directory = list()
            for file in files:
                files_in_directory.append(os.path.join(roots, file))
        return files_in_directory

    def send_entities_to_tms_as_json(self):
        files = self.list_files_in_directory('temp_files/institutions/intro')
        for file in files:
            try:
                payload = {"data": App.encode_file_to_base64(file), "filename": file, "lang_iso": "en"}
                process = self.tms.upload_file(project_id=os.getenv('INSTITUTION_INTRO_CARD_PROJECT'), params=payload)
            # TODO Implement successful feedback.
            except requests.exceptions.RequestException as e:
                print(f"An error occurred while sending the request: {e}")

    def prepare_institutions_for_tms(self, institutions_never_sent_to_tms: tuple, ) -> None:
        keys_available = self.project.key.calculate_keys_from_llm_projects(self.project)
        if keys_available <= self.project.key.allocated_for_llm_reviews:
            for i, institution in enumerate(institutions_never_sent_to_tms):
                data = self.api_client.get_institution_id(institutions_never_sent_to_tms[i][0])
                all_blocks = data[1]['item']['blocks']
                blocks_of_pure_text = {}
                for index, block in enumerate(all_blocks):
                    if len(block) > 1 and block[0] != "<" and block[-1] != ">":
                        blocks_of_pure_text[f'key{index}'] = block
                    self.save_dict_as_json(blocks_of_pure_text, os.path.join('.', 'temp_files', 'institutions', 'intro',
                                                                             f'{institutions_never_sent_to_tms[i][0]}.json'))
        else:
            print('Not enough allocated keys for review.')

    def run(self):
        App.clear_console()
        App.display_welcome_message()
        choice = App.prompt_user(
            "Would you like to process institutions or programs? Type 1 for institutions and 2 for programs.\n")
        entities_never_sent_to_tms = self.handle_choice(choice)
        self.prepare_institutions_for_tms(entities_never_sent_to_tms)
        # self.list_files_in_directory('temp_files/institutions/intro')
        self.send_entities_to_tms_as_json()
        self.db.close()
