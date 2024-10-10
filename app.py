from utilities.functions import *
from classes.db import DB
import requests
from dotenv import load_dotenv
from classes.project import Project
from classes.key import Key
from classes.institution import Institution
from classes.program import Program
import lokalise

load_dotenv()

# Instantiate main classes
tms = lokalise.Client(os.getenv('TMS_TOKEN'))
project = Project(tms)
key = Key(project)
institution = Institution()
program = Program()

print('*** KEG L10N LLM POC ***\n')
institution_or_program = int(
    input("Would you like to process institutions or programs? Type 1 for institutions and 2 for programs.\n"))

if institution_or_program == 1:
    num_of_institutions_to_send_to_tms = int(
        input("Insert the number of institutions you would like to send content for review. The maximum is 500.\n"))
    num_of_institutions_to_send_to_tms = len(range(1, num_of_institutions_to_send_to_tms + 1))
else:
    num_of_programs_to_send_to_tms = int(
        input("Insert the number of programs you would like to send content for review. The maximum is 500.\n"))
    num_of_programs_to_send_to_tms = len(range(1, num_of_programs_to_send_to_tms + 1))

clear_console()

if num_of_institutions_to_send_to_tms > 0:

    db = DB('keg_l10n_llm_poc')

    # Fetch the institution IDs from the SmartHub DB and store those that have not been
    # stored before along with a flag to signalize that they have never been sent to the TMS.
    institutions_in_db = db.query("SELECT id FROM institutions").fetchall()
    latest_institutions = institution.get_all_ids_from_external_db()

    data = list()
    for institution in latest_institutions:
        if all(institution != institution_in_db[0] for institution_in_db in institutions_in_db):
            data.append(tuple((institution, 0)))

    # Insert data with INSERT OR IGNORE to avoid duplicate ID errors
    db.query("INSERT OR IGNORE INTO institutions (id, sent_to_tms) VALUES (?, ?);", data)
    db.commit()
    # Fetch institutions that have never been sent to the TMS
    institutions_never_sent_to_tms = (db.query("SELECT * FROM institutions WHERE sent_to_tms = 0 LIMIT ?",
                                               (num_of_institutions_to_send_to_tms,))
                                      .fetchall())
    db.close()

    keys_from_llm_projects = key.calculate_keys_from_llm_projects()
    # Check first provider.
    # Iterate through each program of provider and send the content of each card to one TMS project
    # Iterate through the provider cards and send the content to one TMS project
    # Once all programs and all institution cards have been sent to the TMS, change the institutions_main_info_sent_to_tms
    # flag to true in the DB.
    # Follow to the next provider and do the same until 30k keys in the TMS have been filled.
    # NOTE: the TMS will segment the blocks further in phrases and those will be saved to the TMs that will later be used
    # as datasets with a maximum of 512 characters per <tu> in the .tmx files
    # NOTE: we need logic that limits that number of entries in the TMs to 30k.

    base_url = 'https://www.studentshub.com/api/sanity'
    institution_list_path = "school-list"
    program_list_path = "program-list"

    # # Main SmartHub endpoints
    institution_list_endpoint = f'{base_url}/{institution_list_path}'
    program_list_endpoint = f'{base_url}/{program_list_path}'

    # Before all else, check if there are enough free keys in the TMS
    if keys_from_llm_projects <= key.allocated_for_llm_reviews:
        for i, institution in enumerate(institutions_never_sent_to_tms):
            #           print(f'Processing institution ID {institutions_never_sent_to_tms[i][0]}')
            #           url = f'{base_url}/institution/{institution}/cards'
            r = requests.get(f'https://www.studentshub.com/api/sanity/school/{institutions_never_sent_to_tms[i][0]}/cards?blocks=true')
            if r.ok:
                data = r.json()
                blocks = data[1]['item']['blocks']
                # Filter out blocks that are pure markup
                blocks_of_pure_text = {}
                for index, block in enumerate(blocks):
                    if len(block) > 1 and block[0] != "<" and block[-1] != ">":
                        blocks_of_pure_text[f'key{index}'] = block
                # Adjust the counter of used keys for LLM reviews
                keys_from_llm_projects = keys_from_llm_projects + len(blocks_of_pure_text)
                print(blocks_of_pure_text)
            else:
                print('Something went wrong.')
# If processing programs
# else:
#         for program_id in num_of_programs_to_send_to_tms:
#             url = f'{base_url}/program/{program_id}/cards?blocks=1'
#             r = requests.get(url)
#             if r.ok:
#                 data = r.json()
#                 blocks = data[0]['item']['blocks']
#                 # Filter blocks that are not pure markup
#                 blocks_of_pure_text = {}
#                 for index, block in enumerate(blocks):
#                     if len(block) > 1 and block[0] != "<" and block[-1] != ">":
#                         blocks_of_pure_text[f'key{index}'] = block
#                 # Adjust the counter of used keys for LLM reviews
#                 # keys_from_llm_projects = keys_from_llm_projects + len(blocks_of_pure_text)
#                     print(blocks_of_pure_text)
#             else:
#                 print('Something went wrong.')
# else:
#     print('Not enough allocated keys. Remove keys and try again.')
