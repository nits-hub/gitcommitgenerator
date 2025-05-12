
"""
Git Commits API with Django REST Framework
This project creates a REST API that fetches git commit data from repositories
without storing it in a database. It supports both remote repositories (GitHub/Bitbucket)
and local repositories.
"""


# Project Structure:
# git_commits_api/
# ├── git_commits_api/
# │   ├── __init__.py
# │   ├── settings.py
# │   ├── urls.py
# │   └── wsgi.py
# ├── commits_api/
# │   ├── __init__.py
# │   ├── apps.py
# │   ├── serializers.py
# │   ├── services/
# │   │   ├── __init__.py
# │   │   ├── git_service.py
# │   │   ├── github_service.py
# │   │   └── bitbucket_service.py
# │   ├── urls.py
# │   └── views.py
# └── manage.py