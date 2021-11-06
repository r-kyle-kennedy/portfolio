from flask import (render_template, redirect,
                    url_for, request)
from models import db, Project, app


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, port=8000, host='0.0.0.0')
