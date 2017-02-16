Contributors Guide
==================

We are happy with any volunteers involvement in `django-konfera <https://github.com/pyconsk/django-konfera>`_ app. If you would like to help us, there are multiple ways to do so. Depending on your skills and type of work you would like to do (doesn’t have to be development), we encourage you to start with any of the following:

Write a blog, get involved on social media or make a talk
---------------------------------------------------------

You can help out by spreading the word about `django-konfera <https://github.com/pyconsk/django-konfera>`_ , or joining `mailing list: django-konfera@pycon.sk <https://groups.google.com/a/pycon.sk/forum/?hl=en#!forum/django-konfera>`_ or `Gitter <https://gitter.im/pyconsk/django-konfera>`_ (if there is Slovak chatter, don't worry just start in English) to help others or share your ideas and experiences with people in community.

Update documentation
--------------------

`GitHub wiki <https://github.com/pyconsk/django-konfera/wiki>`_ is used to guide users and developers the right way. If you don't know how to do something, we probably missed it in our wiki. Documentation is a never ending process so we welcome any improvement suggestions, feel free to create issues in our bug tracker.

If you feel that our documentation needs to be modified or we missed something, feel free to submit PR, or get in touch with us at our `mailing list: django-konfera@pycon.sk <https://groups.google.com/a/pycon.sk/forum/?hl=en#!forum/django-konfera>`_ or `Gitter <https://gitter.im/pyconsk/django-konfera>`_ (if there is Slovak chatter, don't worry just start in English).

Suggest an improvement or report bug
------------------------------------

All issues are handled by `GitHub issue tracker <https://github.com/pyconsk/django-konfera/issues>`_, if you've found a bug please create an issue for it. For security related issues please send GPG encrypted email to `richard.kellner (at) pycon.sk <http://richard.kellnerovci.sk/public-pgp-key.html>`_. `Public GPG key <http://richard.kellnerovci.sk/public-pgp-key.html>`_

If there is something you are missing, and wish to be implemented in `django-konfera <https://github.com/pyconsk/django-konfera>`_, feel free to create an issue and mark it as an enhancement.

Update django-konfera
---------------------

All development is done on `GitHub <https://github.com/pyconsk/django-konfera>`_. If you decide to work on existing issue, **please mention in the issue comment that you are working on it so other people do not work on the same issue**. Create your `fork <https://github.com/pyconsk/django-konfera/fork>`_ and **in new branch update code**. Once you are happy with your changes create `pull request <https://help.github.com/articles/using-pull-requests>`_ and we will review and merge it as soon as we can. To make the life easier please do all your work in a `separate branch <https://git-scm.com/book/en/v1/Git-Branching>`_ (if there are multiple commits we do `squash merge <https://github.com/blog/2141-squash-your-commits>`_), if there is a issue for your change should include the issue number in the branch name and merge request description so they are linked on GitHub. We encourage you to write tests for your code (however this is not required), as we have `continuous integration <https://travis-ci.org/pyconsk/django-konfera>`_ in place. Once you request merge request on GitHub, there will be an automated test run, please make sure each test passes. Sometimes it take few minutes for the Travis CI to start tests, so please be patient. Once the tests are successful, we do run test coverage, that  calculates how much of the code is covered with unit tests, if you add new code without test you lower the coverage and pull request is marked that some checks were not successful. We encourage you to do the best practice and write the tests, but event if you don't we will accept the pull request.

Write a test
------------

We realize that there is never too much testing, so you can help us by creating any form of `automated testing <https://travis-ci.org/pyconsk/django-konfera>`_. You will improve our continuous integration and make the project harder to break.

Getting help
------------

If you look for help, visit our `monthly meetups in Bratislava <https://pycon.sk/sk/meetup.html>`_ or give us a shout at `mailing list: django-konfera@pycon.sk <https://groups.google.com/a/pycon.sk/forum/?hl=en#!forum/django-konfera>`_ or `Gitter <https://gitter.im/pyconsk/django-konfera>`_ (if there is Slovak chatter, don't worry just start in English).

Developer's HowTo
=================

Development standards
---------------------

* We do use standard PEP8, with extended line to 119 characters.
* Each pull request is tested against our automated test suite (yes, PEP8 is one of the tests).
* Writing automated tests for the new code is preferred, but not required.

Development setup
-----------------

You can either follow guide in example directory, but that is most just for testing the app from cloned repo.

This is reusable django app, which means you have to create project first. Create directory and run the following commands (in Linux, or Mac).

1. ``pyvenv envs3`` this will create virtual environments for you, where you can install all requirements needed
2. ``source envs3/bin/activate`` activate virtual environments
3. ``pip install django`` install out main dependency
4. ``django-admin startproject pyconsk`` start your own django project (feel free to name it differently)
5. ``git clone git@github.com:YOUR-GITHUB-ACCOUNT/django-konfera.git`` make a clone of your fork of django-konfera
6. ``cd pyconsk`` lets go inside the project directory
7. ``ln -s ../django-konfera/konfera .`` create a symbolic link to it is in PYTHONPATH and app can be found by Django
8. in pyconsk/settings.py add ``konfera`` into INSTALLED APPS
9. in pyconsk/settings.py add ``konfera.utils.collect_view_data`` into TEMPLATES, context_processors
10. ``url(r'', include('konfera.urls'))`` include konfera urls in project's pyconsk/urls.py file (don't forget from django.conf.ulrs import include)
11. ``python manage.py migrate`` execute migration so it will pre-populate the DB structure
12. ``python manage.py loaddata konfera/fixtures/test_data.json`` insert dummy data into DB
13. ``python manage.py runserver`` start development server, and check the app in browser

Development methodology
-----------------------

1. You create a `fork <https://github.com/pyconsk/django-konfera/fork>`_ of the project (you do this only once. Afterwards you already have it in your GitHub, it is your repo in which you are doing all the development).
2. Clone your fork locally ``git clone git@github.com:YOUR-GITHUB-ACCOUNT/django-konfera.git`` add upstream remote to be able to download updated into your fork ``git remote add upstream https://github.com/pyconsk/django-konfera.git``. You don't have the right to push to upstream, but do regularly pull and push to your fork to keep it up-to-date and prevent conflicts.
3. Pick up a `issue <https://github.com/pyconsk/django-konfera/issues>`_, and make a comment that you are working on it.
4. In your local git copy you create a branch: ``git checkout -b XX-new-feature`` (where XX is issue number).
5. Coding time:

   * Do commit how often you need. At this point doesn't matter if code is broken between commits.
   * Store your change in your repo at GitHub. You can push to server how many times you want: ``git push origin XX-new-feature``.
   * Merge the code from upstream as often as you can: ``git pull upstream master``. At this point we don't care about merge message, or rebase to get rid of it. We will do `squash merge <https://github.com/blog/2141-squash-your-commits>`_ (in upstream master it will looks like one commit).
   * Anytime during development execute ``python manage.py test konfera`` to run all tests, make sure all passes before creating PR.

6. Once you are happy with your code, you click on `pull request <https://help.github.com/articles/using-pull-requests>`_ button, and select master branch in upstream and XX-new-feature branch from your repo. At this point automated tests will be run if everything is OK, if you see some errors please fix them and push your fix into your branch. This way the pull request is updated with fixes and tests are run again.
7. In case reviewer asks for changes you can do all the things mentioned in point 5. Once happy with the changes make a note in pull request to review again.
8. Your feature is approved and merged to master of upstream, so you can check out master at your local copy: ``git checkout master`` and pull the newly approved changes from upstream ``git pull upstream master``. Pull from upstream will download your work (as one commit into master) that has been done in branch. Now you can delete your local branch ``git branch --delete XX-new-feature``, and also remote one ``git push origin :XX-new-feature``

Continuous Integration
----------------------

Once developer changes create `pull request <https://help.github.com/articles/using-pull-requests>`_ we do automated test for supported Python and Django versions and execute all unit tests in our `Travis CI <https://travis-ci.org/pyconsk/django-konfera>`_. Once the pull request is merged to the master `staging server <https://staging.pycon.sk>`_ is updated automatically, so you can see your changes in project on server immediately.
