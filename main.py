import sys

from config import Configuration
from todoist.api import TodoistAPI
import json


class Todoist:

    def __init__(self, config, ignore_closed_todos=False):
        self.api = TodoistAPI(config.api_key)
        self.project_name = config.project_name
        self.section_name = config.new_section_name
        self.ignore_closed_todos = ignore_closed_todos

        self.api.sync()
        self.__init_project()
        self.__init_section()

    def discover(self):
        self.__discover_labels()
        self.__discover_projects()

    def __discover_labels(self):
        print("Labels")
        for label in self.api.labels.all():
            print(f"  {label['id']}: \"{label['name']}\"")

    def __discover_projects(self):
        print("Projects")
        for project in self.api.projects.all():
            print(f"  {project['id']}: \"{project['name']}\"")

    def update_issues(self, issues):
        for i, issue in enumerate(issues):
            print(f"Updating issue {issue.issue_id}")
            if self.__project_contains_issue(issue.issue_id):
                print("\talready present")
            else:
                self.api.items.add(f"{issue.issue_subject} ([#{issue.issue_id}](https://redmine.ao-intranet/issues/{issue.issue_id}))", project_id=self.project_id, section_id=self.section_id)
                print("\tissue added")

            # Request limit of 100 commands per request
            if i >= 95:
                self.api.commit()

        self.api.commit()

    def __init_project(self):
        matching_projects = list(filter(lambda p: p['name'] == self.project_name, self.api.state['projects']))

        project = self.__ensure_exactly_one(matching_projects, 'project')
        self.project_id = matching_projects[0]['id']
        print(f"Found project <{self.project_name}> with id <{self.project_id}>")

    def __init_section(self):
        sections = self.api.projects.get_data(self.project_id)['sections']
        matching_sections = list(filter(lambda s: s['name'] == self.section_name, sections))

        section = self.__ensure_exactly_one(matching_sections, 'section')
        self.section_id = section['id']
        print(f"Found section <{self.section_name}> with id <{self.section_id}>")

    def __ensure_exactly_one(self, list, item_name):
        the_len = len(list)
        if the_len != 1:
            raise Exception(f"Expected to find exactly one of {item_name}, but found {the_len}")

        return list[0]

    def __project_contains_issue(self, issue_id):
        items = self.api.projects.get_data(self.project_id)['items']

        item_finder = lambda i: f"[#{issue_id}]" in i['content']

        matching_open_items = list(filter(item_finder, items))

        if len(matching_open_items) > 0:
            return True

        if self.ignore_closed_todos:
            return False

        matching_closed_items = self.api.completed.get_all(project_id=self.project_id)['items']
        return len(list(filter(item_finder, matching_closed_items))) > 0

class Issue:
    def __init__(self, issue_id, issue_subject):
        self.issue_id = issue_id
        self.issue_subject = issue_subject

def main():
    config = Configuration()
    todoist = Todoist(config, ignore_closed_todos=True)

    if '--discover' in sys.argv:
        todoist.discover()
        return

    with open('issues.json', encoding='utf-8') as issues_file:
        data = json.load(issues_file)

        issues = list(map(lambda i: Issue(i['id'], i['subject']), data['issues']))
    todoist.update_issues(issues)

if __name__ == '__main__':
    main()
