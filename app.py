from flask import (render_template, redirect,
                    url_for, request, session)
from urllib.request import urlopen
import json
import datetime
import os
from dotenv import load_dotenv
from models import db, Project, app

load_dotenv()

ADMIN_USERNAME = os.environ.get("PORTFOLIO_ADMIN_USERNAME")
ADMIN_PASSWORD = os.environ.get("PORTFOLIO_ADMIN_PASSWORD")
app.secret_key = os.environ.get("PORTFOLIO_SECRET_KEY")


def format_date(date_str):
    date = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    return date


def require_admin():
    return session.get("is_admin", False)


def edit_project_from_gh(project, repo):
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
                edit_project_from_gh(project, repo)
        db.session.commit()
    except Exception as e:
        print(e)


@app.route('/')
def index():
    projects = Project.query.all()
    return render_template('index.html', projects=projects)


@app.route('/login', methods=['GET', 'POST'])
def login():
    projects = Project.query.all()
    if request.method == 'POST':
        if request.form.get('username') == ADMIN_USERNAME and request.form.get('password') == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect(url_for('index'))
    session.pop('is_admin', None)
    return render_template('login.html', projects=projects)


@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))


@app.route('/project/<id>')
def project(id):
    projects = Project.query.all()
    project = Project.query.get_or_404(id)
    return render_template('detail.html', project=project, projects=projects)


@app.route('/project/<id>/edit', methods=['GET', 'POST'])
def edit_project(id):
    if not require_admin():
        return redirect(url_for('login'))

    projects = Project.query.all()
    project = Project.query.get_or_404(id)
    if request.form:
        project.title=request.form['title']
        project.date=datetime.datetime.strptime(request.form['date'], "%Y-%m")
        project.description=request.form['desc']
        project.skills=request.form['skills']
        project.url=request.form['github']
        project.gh_id = request.form['gh_id']
        db.session.commit()
        return redirect(url_for('project', id=project.id))
    return render_template('projecteditform.html', project=project, projects=projects)


@app.route('/projects/update/<id>')
def update(id):
    if not require_admin():
        return redirect(url_for('login'))

    add_github_api()
    return redirect(url_for('project', id=id))


@app.route('/delete/<id>')
def delete(id):
    if not require_admin():
        return redirect(url_for('login'))

    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/project/new', methods=['GET', 'POST'])
def add_project():
    if not require_admin():
        return redirect(url_for('login'))

    projects = Project.query.all()
    if request.form:
        new_project = Project(title=request.form['title'], date=datetime.datetime.strptime(request.form['date'], "%Y-%m"),
                        description=request.form['desc'], skills=request.form['skills'],
                        url=request.form['github'], gh_id = request.form['gh_id'])
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for('project', id=new_project.id))
    return render_template('projectform.html', projects=projects)


@app.route('/about')
def about():
    projects = Project.query.all()
    return render_template('about.html', projects=projects)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', msg=error), 404


if __name__ == '__main__':
    db.create_all()
    add_github_api()
    app.run(debug=True, port=8000, host='0.0.0.0')
