class Institution:

    def __init__(self, api_client, institution_id: int = None, sent_to_tms: bool = False):
        self.api_client = api_client
        self.institution_id = institution_id
        self.sent_to_tms = sent_to_tms

    @classmethod
    def load(cls, db, institution_id):
        query = "SELECT id, sent_to_tms FROM institutions WHERE id = ?"
        result = db.query(query, (institution_id,)).fetchone()

        if result:
            # Create an instance of Institution with the fetched data
            return cls(cls.api_client, institution_id=result[0], sent_to_tms=result[1])
        else:
            # If no institution found, return None or handle accordingly
            return None

    def fetch_all_ids_from_external_db(self) -> list:
        all_institution_ids = self.get_institution_ids()
        return all_institution_ids

    @classmethod
    def get_number_of_institutions(cls) -> int:
        return len(cls.fetch_all_ids_from_external_db())

    def get_institution_ids(self) -> list:
        return self.api_client.get(path='school-list')
