from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime
import os


app = Flask(__name__)
# Use DATABASE_URL env var (e.g. Postgres on Render) with a sqlite fallback for local dev
database_url = os.environ.get('DATABASE_URL', 'sqlite:///projects.db')
# Normalize old-style Heroku URLs
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column('Title', db.String())
    date = db.Column('Date', db.DateTime, default=datetime.datetime.now)
    description = db.Column('Description', db.Text)
    skills = db.Column('Skills', db.Text)
    url = db.Column('URL', db.Text)
    gh_id = db.Column('GitHub Repo ID', db.Integer)


    def __repr__(self):
        return f'''<Project (Title: {self.title}
                Date: {self.date}
                Description: {self.description}
                Skills: {self.skills}
                URL: {self.url})'''
