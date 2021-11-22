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
    project.title = repo['name']
    project.date = format_date(repo['updated_at'])
    project.description = repo['description']
    project.skills = ', '.join(repo['topics'])
    project.url = repo['html_url']



def add_github_api():
    try:
        url = "https://api.github.com/users/r-kyle-kennedy/repos"
        response = urlopen(url)
        data = json.loads(response.read())
        for repo in data:
            project_in_db = db.session.query(Project).filter(Project.gh_id==repo['id']).one_or_none()
            if not project_in_db:
                new_project = Project(title = repo['name'],
                date = format_date(repo['updated_at']),
                description = repo['description'],
                skills = ', '.join(repo['topics']),
                url = repo['html_url'],
                gh_id = repo['id'])
                db.session.add(new_project)
            else:
                project = db.session.query(Project).filter(Project.gh_id==repo['id']).first()
                edit_project(project, repo)
        db.session.commit()
    except Exception as e:
        print(e)


@app.route('/')
def index():
    projects = Project.query.all()
    return render_template('index.html', projects=projects)


@app.route('/projects/<id>')
def project(id):
    projects = Project.query.all()
    project = Project.query.get_or_404(id)
    return render_template('detail.html', project=project, projects=projects)


@app.route('/projects/update/<id>')
def update(id):
    add_github_api()
    return redirect(url_for('project', id=id))


if __name__ == '__main__':
    db.create_all()
    add_github_api()
    app.run(debug=True, port=8000, host='0.0.0.0')
