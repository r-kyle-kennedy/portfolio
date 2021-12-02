# Portfolio
Portfolio website using flask and a SQLAlchemy database.

The database is created using github's user api. In order for the site to pull the correct information change the url found in app.py. The database is built using each public repo's name, date, descripion, topics, and url.

## To run this site locally:
1. Clone the repo
2. Once inside the project folder create a virtual environment using `python -m venv env`
3. Now activate your virtual environment using `source ./env/bin/activate` on Mac/Linux or `.\env\Scripts\activate` on Windows
4. Once inside the virtual environment use `pip install -r requirements.txt` to install the necessary python packages.
5. After the install finishes, run the server using `python app.py` and then ctrl+click on the url that loads in the terminal.


## What I learned:
This project helped me to really understand the fundamentals of creating, updating, and maintaining a clean database both through adding entries myself and updating it through the github api. I was glad to see that reading in the api and adding the information to the database was relatively straight forward.
Using the provided templates and using flask to wire everything together allowed me to gain a firm understanding of how Flask works and how I could use it to add my own stretch goals.
