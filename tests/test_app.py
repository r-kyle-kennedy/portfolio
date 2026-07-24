import datetime
import json
import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app as app_module
import pytest
from flask import session, url_for

from app import (app, add_github_api, edit_project_from_gh,
                 format_date, require_admin)
from models import Project, db

app.config.update(
    TESTING=True,
    SECRET_KEY='test-secret',
    SQLALCHEMY_DATABASE_URI='sqlite:///tests/test_projects.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)
app.secret_key = app.config['SECRET_KEY']


@pytest.fixture(scope='module', autouse=True)
def app_context():
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()
        db_path = os.path.join(os.path.dirname(__file__), 'test_projects.db')
        if os.path.exists(db_path):
            os.remove(db_path)


@pytest.fixture(scope='module')
def test_client():
    return app.test_client()


@pytest.fixture(autouse=True)
def clean_db():
    yield
    db.session.rollback()
    Project.query.delete()
    db.session.commit()


def test_format_date_parses_utc_timestamp():
    parsed = format_date('2022-01-01T12:00:00Z')

    assert parsed == datetime.datetime(2022, 1, 1, 12, 0, 0)


def test_require_admin_reads_session_flag():
    with app.test_request_context('/'):
        assert require_admin() is False

        session['is_admin'] = True
        assert require_admin() is True


def test_edit_project_from_gh_updates_project_fields():
    project = Project(
        title='old',
        date=datetime.datetime(2020, 1, 1),
        description='old',
        skills='old',
        url='old',
    )

    repo = {
        'name': 'new-name',
        'updated_at': '2023-03-03T13:45:00Z',
        'description': 'new description',
        'topics': ['python', 'flask'],
        'html_url': 'https://github.com/example/new-name',
    }

    edit_project_from_gh(project, repo)

    assert project.title == 'new-name'
    assert project.date == datetime.datetime(2023, 3, 3, 13, 45, 0)
    assert project.description == 'new description'
    assert project.skills == 'python, flask'
    assert project.url == 'https://github.com/example/new-name'


class FakeGithubResponse:
    def __init__(self, payload):
        self.payload = payload

    def read(self):
        return json.dumps(self.payload).encode('utf-8')


def test_add_github_api_creates_and_updates_projects():
    app.ADMIN_USERNAME = 'admin'
    app.ADMIN_PASSWORD = 'secret'

    sample_repos = [
        {
            'id': 1,
            'name': 'repo-one',
            'updated_at': '2023-01-01T10:00:00Z',
            'description': 'First repo',
            'topics': ['first', 'test'],
            'html_url': 'https://github.com/example/repo-one',
        },
        {
            'id': 2,
            'name': 'repo-two',
            'updated_at': '2023-02-01T11:00:00Z',
            'description': 'Second repo',
            'topics': ['second'],
            'html_url': 'https://github.com/example/repo-two',
        },
    ]

    with patch('app.urlopen', return_value=FakeGithubResponse(sample_repos)):
        add_github_api()

    projects = Project.query.order_by(Project.gh_id).all()
    assert len(projects) == 2
    assert projects[0].title == 'repo-one'
    assert projects[0].skills == 'first, test'
    assert projects[1].title == 'repo-two'

    sample_repos[0]['description'] = 'Updated first repo'
    sample_repos[0]['topics'] = ['updated']

    with patch('app.urlopen', return_value=FakeGithubResponse(sample_repos)):
        add_github_api()

    updated = Project.query.filter_by(gh_id=1).one()
    assert updated.description == 'Updated first repo'
    assert updated.skills == 'updated'


def test_index_route_renders_homepage(test_client):
    response = test_client.get('/')
    assert response.status_code == 200
    assert b'Portfolio' in response.data or b'<html' in response.data


def test_login_route_authenticates_and_redirects(test_client):
    app_module.ADMIN_USERNAME = 'admin'
    app_module.ADMIN_PASSWORD = 'secret'

    response = test_client.post('/login', data={
        'username': 'admin',
        'password': 'secret',
    })

    assert response.status_code == 302
    assert response.headers['Location'] is not None
    assert '/login' not in response.headers['Location']


def test_logout_route_clears_admin_session(test_client):
    with test_client.session_transaction() as test_session:
        test_session['is_admin'] = True

    response = test_client.get('/logout')

    assert response.status_code == 302
    with test_client.session_transaction() as test_session:
        assert 'is_admin' not in test_session


def test_add_project_route_requires_admin_and_creates_project(test_client):
    with test_client.session_transaction() as test_session:
        test_session['is_admin'] = True

    response = test_client.post(
        '/project/new',
        data={
            'title': 'New Project',
            'date': '2024-01',
            'desc': 'Test description',
            'skills': 'python, flask',
            'github': 'https://github.com/example/new-project',
            'gh_id': '100',
        },
    )

    assert response.status_code == 302
    created = Project.query.filter_by(gh_id=100).one_or_none()
    assert created is not None
    assert created.title == 'New Project'


def test_edit_project_route_updates_existing_project(test_client):
    project = Project(
        title='Edit me',
        date=datetime.datetime(2023, 1, 1),
        description='Original',
        skills='python',
        url='https://example.com',
        gh_id=200,
    )
    db.session.add(project)
    db.session.commit()

    with test_client.session_transaction() as test_session:
        test_session['is_admin'] = True

    response = test_client.post(
        f'/project/{project.id}/edit',
        data={
            'title': 'Edited Title',
            'date': '2024-02',
            'desc': 'Updated description',
            'skills': 'flask, testing',
            'github': 'https://github.com/example/edited',
            'gh_id': '200',
        },
    )

    assert response.status_code == 302
    updated = Project.query.get(project.id)
    assert updated.title == 'Edited Title'
    assert updated.description == 'Updated description'
    assert updated.skills == 'flask, testing'


def test_delete_route_removes_project(test_client):
    project = Project(
        title='Delete me',
        date=datetime.datetime(2023, 1, 1),
        description='Delete',
        skills='delete',
        url='https://example.com',
        gh_id=300,
    )
    db.session.add(project)
    db.session.commit()

    with test_client.session_transaction() as test_session:
        test_session['is_admin'] = True

    response = test_client.get(f'/delete/{project.id}')
    assert response.status_code == 302
    assert Project.query.get(project.id) is None


def test_update_route_triggers_github_sync(test_client):
    project = Project(
        title='Update me',
        date=datetime.datetime(2023, 1, 1),
        description='Original',
        skills='sync',
        url='https://example.com',
        gh_id=400,
    )
    db.session.add(project)
    db.session.commit()

    with test_client.session_transaction() as test_session:
        test_session['is_admin'] = True

    with patch('app.add_github_api') as mocked_add_github_api:
        response = test_client.get(f'/projects/update/{project.id}')

    assert response.status_code == 302
    mocked_add_github_api.assert_called_once()


def test_not_found_handler_returns_404(test_client):
    response = test_client.get('/project/999999')
    assert response.status_code == 404
    assert b'404' in response.data
