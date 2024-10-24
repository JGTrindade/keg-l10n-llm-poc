from classes.tms import TMS
from classes.key import Key


class Project:
    def __init__(self, tms: TMS):
        self.tms = tms
        self.key = Key()

    def get_project_names(self) -> list[str]:
        project_names = []
        projects = self.tms.fetch_projects()
        for project in projects.items:
            project_names.append(project.name)
        return project_names

    def get_llm_projects(self) -> list:
        project_prefix = 'LLM Reviews'
        llm_projects = []

        projects = self.tms.fetch_projects().items
        for i in range(len(projects)):
            if project_prefix in projects[i].name:
                llm_projects.append(projects[i])
        return llm_projects
