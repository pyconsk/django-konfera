##Example Project for django-konfera

This example is provided as a convenience feature to allow potential users to try the app straight from the app repo without having to create a django project.

It can also be used to develop the app in place.

Prerequisites to beginning development:
  - python3 and sqlite3 installed.
  - We suggest using [`pyvenv`](https://docs.python.org/3/library/venv.html) to setup a virtualenv for the project (to isolate project-specific dependencies from the rest of your system)

To run this example, follow these instructions:

1. Navigate to the `example` directory

2. Install the requirements for the package:

  `pip install -r requirements.txt`

3. Make and apply migrations

  `python manage.py makemigrations`

  `python manage.py migrate`

4. Load test data into the database. Run the following command from the root of the project:

  `python manage.py loaddata ../konfera/fixtures/test_data.json`

5. Run the server

  `python manage.py runserver`

6. Access from the browser at `http://127.0.0.1:8000`. An example url to test is `http://127.0.0.1:8000/events/` which should take you to the event listing page with loaded test data.

To manage this example, you can do following:

* Create admin user and access admin area in browser at `http://127.0.0.1:8000`:

  `python manage.py createsuperuser`

To run the tests, you can do following:

  `python manage.py test konfera`

If you have decided to contribute, please read our [contributing guide](https://github.com/pyconsk/django-konfera/blob/master/CONTRIBUTING.rst).
