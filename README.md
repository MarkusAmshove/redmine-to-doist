# redmine-to-doist

Small tool to synchronize Redmine issues to a todoist project.

## Features

* Synchronize Redmine issues to a specific todoist project
* Add todoist labels based on Redmine issue tracker
* Add todoist labels based on Redmine project
* Add items to specific lanes based on issue status

## Usage

```shell
$ pip install -r requirements.txt
$ TODOIST_API=<apikey> python main.py
```

Currently there is no direct synchronization with Redmine. In order to use this, there is a file called `issues.json` to sit beside the `main.py` file.
This json file simply contains the output of a Redmine API-call, e.g. `https://my-redmine.com/issues.json?assigned_to_id=me`.

## Configuration

The behavior can be controlled via the `config.json` file.

Example:

```
{
  "project_name": "Redmine", // Project name within Todoist to sync the issues to
  "fallback_section_name": "Backlog", // Section which issues are added to when no section mapping fits
  "closed_issue_section": "Feature", // The section where closed issues (e.g. items which are no longer within the issues.json) are moved to
  "mappings": {
    "tracker": { // Mapping from issue tracker to todoist label
      "Feature": 2156508899 // Maps the redmine tracker `Feature` to todoist label with id 2156508899
    },
    "projects": {
      "DevOps": 2155441501 // Maps the redmine project `DevOps` to label with id 2155441501
    }
  }
}
```

To find the ids of todoist labels, run with program with the `--discover` flag:

```shell
$ TODOIST_API=<apikey> python main.py --discover
Labels
  2155441501: "DevOps🐳"
```