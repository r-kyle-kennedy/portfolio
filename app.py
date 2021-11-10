from flask import (render_template, redirect,
                    url_for, request)
from urllib.request import urlopen
import json
import datetime

from models import db, Project, app


def format_date(date_str):
    date = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    return date


def edit_project(project, repo):
    project.date = format_date(repo['updated_at'])
    project.description = repo['description']
    project.skills = ','.join(repo['topics'])
    project.url = repo['html_url']



def add_github_api(data):
    for repo in data:
        project_in_db = db.session.query(Project).filter(Project.title==repo['name']).one_or_none()
        if not project_in_db:
            new_project = Project(title = repo['name'],
                        date = format_date(repo['updated_at']),
                        description = repo['description'],
                        skills = ','.join(repo['topics']),
                        url = repo['html_url'])
            db.session.add(new_project)
        else:
            project = db.session.query(Project).filter(Project.title==repo['name']).first()
            edit_project(project, repo)
    db.session.commit()


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    db.create_all()
    url = "https://api.github.com/users/r-kyle-kennedy/repos"
    response = urlopen(url)
    data = json.loads(response.read())
    add_github_api(data)
    # app.run(debug=True, port=8000, host='0.0.0.0')
