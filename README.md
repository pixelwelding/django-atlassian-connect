# django-atlassian-connect
Django-atlassian-connect allows you to build a Atlassian Connect apps using Django

## Installation
Download and install using ``pip install django-atlassian-connect``
```
$ pip install django-atlassian-connect
```

## Development
The project is based in `poetry` dependency management and packaging system. The basic steps are

Install poetry
```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

Install the dependencies
```
poetry install
```

Install your development pre-commit hooks
```
poetry run pre-commit install
```

Testing
```
poetry run tox
```

Documentation
```
poetry run sphinx-build docs/source/ docs/build/
```

## Contributing
If you'd like to contribute, the best approach is to send a well-formed pull
request, complete with tests and documentation. Pull requests should be
focused: trying to do more than one thing in a single request will make it more
difficult to process.

