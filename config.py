import json
import os

class Configuration:

    def __init__(self):
        self.todoist_api_key = os.environ.get['TODOIST_API']
        if self.todoist_api_key == None:
            raise Exception('Todoist API-Key not set via environment variable <TODOIST_API>')

        with open('config.json', encoding='utf-8') as config_file:
            configuration = json.load(config_file)


