from classes.tms import TMS


class Project:
    def __init__(self, tms_client: TMS.client):
        self.tms_client = tms_client

    def get_projects(self):
        projects = self.tms_client.projects()
        return projects

    def get_project_names(self) -> list[str]:
        project_names = []
        projects = self.get_projects()
        for project in projects.items:
            project_names.append(project.name)
        return project_names

    def get_llm_projects(self) -> list:
        project_prefix = 'LLM Reviews'
        llm_projects = []

        projects = self.get_projects().items
        for i in range(len(projects)):
            if project_prefix in projects[i].name:
                llm_projects.append(projects[i])
        return llm_projects
