class Key:
    def __init__(self):
        self._max_number = 50000
        self._allocated_for_llm_reviews = 30000

    @property
    def max_number(self):
        return self._max_number

    @property
    def allocated_for_llm_reviews(self):
        return self._allocated_for_llm_reviews

    def calculate_keys_from_llm_projects(self, project) -> int:
        llm_keys = 0
        llm_projects = project.get_llm_projects()

        for i in range(len(llm_projects)):
            llm_keys = llm_keys + llm_projects[i].statistics['keys_total']
        return llm_keys
