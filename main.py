import sys

from config import Configuration
from todoist.api import TodoistAPI
import json
import re


class Todoist:

    def __init__(self, config, ignore_closed_todos=False):
        self.config = config
        self.api = TodoistAPI(config.api_key)
        self.project_name = config.project_name
        self.ignore_closed_todos = ignore_closed_todos

        self.api.sync()
        self.__init_project()
        self.__init_sections()

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
        for issue in issues:
            print(f"Updating issue {issue.issue_id}")
            existing_issue_item = self.__find_issue(issue.issue_id)
            labels = self.__find_labels_for_issue(issue)
            section = self.__find_section_id_for_status(issue.issue_status)
            if existing_issue_item is not None:
                self.__update_issue(existing_issue_item, section, labels)
            else:
                self.api.items.add(
                    f"{issue.issue_subject} ([#{issue.issue_id}](https://redmine.ao-intranet/issues/{issue.issue_id}))",
                    project_id=self.project_id,
                    section_id=section,
                    labels=labels)
                print("\tissue added")

            # Request limit of 100 commands per request
            if len(self.api.queue) >= 95:
                self.api.commit()

        self.__move_closed_issues(issues)
        self.api.commit()

    @staticmethod
    def __update_issue(item, section, labels):
        updated = False
        if sorted(labels) != sorted(item['labels']):
            item.update(
                labels=labels,
            )
            updated = True

        if item['section_id'] != section:
            item.move(
                section_id=section
            )
            updated = True

        if updated:
            print('  issue updated')

    def __find_labels_for_issue(self, issue):
        tracker_name = issue.issue_tracker
        mapped_tracker_label_id = self.config.tracker_mapping.get(tracker_name)

        labels = []
        if mapped_tracker_label_id is not None:
            labels.append(mapped_tracker_label_id)

        mapped_project_id = self.config.project_mapping.get(issue.project_name)
        if mapped_project_id is not None:
            labels.append(mapped_project_id)

        return labels

    def __find_section_id_for_status(self, status_name):
        section_id = self.sections.get(status_name)
        if section_id is None:
            print(f"No section found for status <{status_name}>, using fallback")
            section_id = self.sections.get(self.config.fallback_section_name)

        return section_id

    def __init_project(self):
        matching_projects = list(filter(lambda p: p['name'] == self.project_name, self.api.state['projects']))

        project = self.__ensure_exactly_one(matching_projects, 'project')
        self.project_id = project['id']
        print(f"Found project <{self.project_name}> with id <{self.project_id}>")

    def __init_sections(self):
        sections = self.api.projects.get_data(self.project_id)['sections']

        self.sections = {}
        for section in sections:
            self.sections[section['name']] = section['id']

    @staticmethod
    def __ensure_exactly_one(items, item_name):
        the_len = len(items)
        if the_len != 1:
            raise Exception(f"Expected to find exactly one of {item_name}, but found {the_len}")

        return items[0]

    def __find_issue(self, issue_id):
        items = self.api.projects.get_data(self.project_id)['items']

        item_finder = lambda i: f"[#{issue_id}]" in i['content']

        matching_open_items = list(filter(item_finder, items))

        if len(matching_open_items) > 0:
            return self.api.items.get_by_id(matching_open_items[0]['id'])

        if self.ignore_closed_todos:
            return None

        matching_closed_items = list(
            filter(item_finder, self.api.completed.get_all(project_id=self.project_id)['items'])
        )
        if len(matching_closed_items) > 0:
            return self.api.items.get_by_id(matching_closed_items[0]['id'])
        return None

    def __move_closed_issues(self, all_issues):
        all_items = self.api.projects.get_data(self.project_id)['items']
        closed_section_id = self.__find_section_id_for_status(self.config.closed_issue_section)
        for item in all_items:
            match = re.search('\\[#(\\d+)\\]\\(', item['content'])
            issue_id = int(match.group(1))
            open_issues = list(map(lambda i: i.issue_id, all_issues))
            if issue_id not in open_issues:
                self.api.items.move(
                    item['id'],
                    section_id=closed_section_id
            )

            if len(self.api.queue) >= 95:
                self.api.commit()


class Issue:
    def __init__(self, issue_id, issue_subject, issue_status, issue_tracker, project_name):
        self.issue_id = issue_id
        self.issue_subject = issue_subject
        self.issue_status = issue_status
        self.issue_tracker = issue_tracker
        self.project_name = project_name


def main():
    config = Configuration()
    todoist = Todoist(config, ignore_closed_todos=True)

    if '--discover' in sys.argv:
        todoist.discover()
        return

    with open('issues.json', encoding='utf-8') as issues_file:
        data = json.load(issues_file)

        issues = list(map(
            lambda i: Issue(i['id'], i['subject'], i['status']['name'], i['tracker']['name'], i['project']['name']),
            data['issues']))
    todoist.update_issues(issues)


if __name__ == '__main__':
    main()
