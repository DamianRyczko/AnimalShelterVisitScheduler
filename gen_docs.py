import os, pathlib, django, pdoc

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AnimalShelterVisitScheduler.settings")
django.setup()

pdoc.pdoc("core", "user_login", output_directory=pathlib.Path("docs"))