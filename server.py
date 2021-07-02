from flask import Flask, render_template, flash, request
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from config import Configuration
from main import update_todoist
import os

secret_key = os.environ.get('FLASK_SECRET_KEY')
if secret_key is None:
    raise Exception('FLASK_SECRET_KEY not set via environment variable')
config = Configuration('config.json')

app = Flask("td")
app.config.from_object(__name__)
app.config['SECRET_KEY'] = secret_key

class IssuesJsonForm(Form):
    issues = TextField('Issues:', validators=[validators.required()])

@app.route("/", methods=['GET', 'POST'])
def issues_form():
    form = IssuesJsonForm(request.form)

    if request.method == 'POST' and form.validate():
        issues = form.issues.data
        print(issues)
        update_todoist(config, issues)

        return "Updated"

    return render_template('issues.html', form=form)

if __name__ == '__main__':
    app.run()
