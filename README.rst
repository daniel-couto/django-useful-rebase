====================
django-useful-rebase
====================

django-useful-rebase is a Django app to add useful behaviour and control to django base models. For each model we apply some design patterns to facilitate replication and use of the DRY principle.

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "django_rebase" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...,
        "django_useful_rebase",
    ]

2. Include the django_rebase URLconf in your project urls.py like this::

    path("django_rebase/", include("django_useful_rebase.urls")),

3. Run ``python manage.py migrate`` to create the models.

4. Inherit your models from django_rebase.ModelBase instead of traditional models.Model.

5. Ready to go. Now you can visit the docs page to check all the added functionalities.

6. please remember: this project is in alpha development and is maintained by a "team of 1" (at least until this update). Be patient and report any bugs and I'll visit them to deliver solutions in new versions asap.