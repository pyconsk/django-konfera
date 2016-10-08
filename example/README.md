##Example Project for django-konfera

This example is provided as a convenience feature to allow potential users to try the app straight from the app repo without having to create a django project.

It can also be used to develop the app in place.

Prerequisites to beginning development: python3 and sqlite3 installed

To run this example, follow these instructions:

0. Install [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/) via pip, and create a new virtualenv with the following command:

  `virtualenv -p /path/to/python3 venv`

Then run `source venv/bin/activate` to start the virtualenv wrapper for the project.

1. Navigate to the `example` directory

2. Install the requirements for the package:

  `pip install -r requirements.txt`

3. Make and apply migrations

  `python manage.py makemigrations`

  `python manage.py migrate`

4. Load test data into the database. Run the following command from the root of the project:

  `python manage.py loaddata konfera/fixtures/test_data.json`

5. Run the server

  `python manage.py runserver`

6. Access from the browser at `http://127.0.0.1:8000`. An example url to test is `http://127.0.0.1:8000/events/` which should take you to the event listing page with loaded test data
