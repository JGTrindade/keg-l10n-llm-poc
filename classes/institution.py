import requests


class Institution:
    institution_list_endpoint = 'https://www.studentshub.com/api/sanity/school-list'

    def __init__(self, institution_id: int = None, sent_to_tms: bool = False):
        self.institution_id = institution_id
        self.sent_to_tms = sent_to_tms
        self.institution_blocks_endpoint = f'https://www.studentshub.com/api/sanity/school/{self.institution_id}/cards?blocks=true'

    @classmethod
    def load(cls, db, institution_id):
        query = "SELECT id, sent_to_tms FROM institutions WHERE id = ?"
        result = db.query(query, (institution_id,)).fetchone()

        if result:
            # Create an instance of Institution with the fetched data
            return cls(institution_id=result[0], sent_to_tms=result[1])
        else:
            # If no institution found, return None or handle accordingly
            return None

    @classmethod
    def get_all_ids_from_external_db(cls) -> list:
        r = requests.get(cls.institution_list_endpoint)
        if r.ok:
            institutions = r.json()
            all_institution_ids = institutions
            return all_institution_ids

    @classmethod
    def get_number_of_institutions(cls) -> int:
        return len(cls.get_all_ids_from_external_db())
