# Portfolio
Portfolio website using flask and a SQLAlchemy database.

The database is created using Github's user API. In order for the site to pull the correct information change the URL found in app.py. The database is built using each public repo's name, date, description, topics, and URL.

## To run this site locally:
1. Clone the repo
2. Once inside the project folder create a virtual environment using `python -m venv env`
3. Now activate your virtual environment using `source ./env/bin/activate` on Mac/Linux or `.\env\Scripts\activate` on Windows
4. Once inside the virtual environment use `pip install -r requirements.txt` to install the necessary python packages.
5. After the install finishes, run the server using `python app.py` and then ctrl+click on the url that loads in the terminal.

## Environment variables
Create a `.env` file with your admin credentials and secret key:

```env
PORTFOLIO_ADMIN_USERNAME=youradmin
PORTFOLIO_ADMIN_PASSWORD=yourpassword
PORTFOLIO_SECRET_KEY=your-long-random-secret-value
```

## Deploying to PythonAnywhere
1. Upload this project to your PythonAnywhere account.
2. In the PythonAnywhere Web tab, configure your virtualenv and static file paths.
3. Set the WSGI configuration file to import `application` from `wsgi.py`.
4. Add environment variables in the PythonAnywhere Web tab, or keep them in `.env` if your app loads it.
5. Make sure `DEBUG` is disabled in production.

If you use the PythonAnywhere WSGI file, set the source to:

```python
from app import app as application
```

Then reload the web app.

## Running tests:
1. Activate the virtual environment.
2. Install developer dependencies with `pip install -r requirements-dev.txt`.
3. Run `pytest` from the project root.

## What I learned:
This project helped me to really understand the fundamentals of creating, updating, and maintaining a clean database both through adding entries myself and updating it through the github api. I was glad to see that reading in the api and adding the information to the database was relatively straight forward.
Using the provided templates and using flask to wire everything together allowed me to gain a firm understanding of how Flask works and how I could use it to add my own stretch goals.


## To see a live version of this site please visit: http://rkylekennedy.pythonanywhere.com/
