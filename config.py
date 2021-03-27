import json
import os

class Configuration:

    def __init__(self):
        self.api_key = os.environ.get('TODOIST_API')
        if self.api_key is None:
            raise Exception('Todoist API-Key not set via environment variable <TODOIST_API>')

        with open('config.json', encoding='utf-8') as config_file:
            configuration = json.load(config_file)
            self.project_name = configuration['project_name']
            self.fallback_section_name = configuration['fallback_section_name']
            self.tracker_mapping = configuration['mappings']['tracker']
            self.closed_issue_section = configuration['closed_issue_section']


