Backlog tracking tool

# Repository

Backlog tracking tool is a home assignment test project written for 
[DareWise][darewise] for Python Developer position.

Assignment Assumptions: 
- Backlog Keys, i.e. "EpicA", "EpicB", etc. are unique, as this is a dictionary. 
- Backlog is properly formatted, i.e. there's no circular references.

The repository follows [Conventional Commits][conventional-commits] 
and uses [GitLab CI](./.gitlab-ci.yaml) for continuous integration.


## Stack

DevEnv tools:
- `poetry`: dependency & devenv management
- `.gitlab-ci.yml`: GitLab flavored CI/CD pipeline for build & deploy

Python tools: 
- `black`: Uncompromising Python code formatter 
- `isort`: Library to sort imports
- `flake8`: Style guide Enforcement
- `mypy`: Optional static type checker for Python
- `pytest`: Framework to write small, readable tests
- `poetry`: Dependency & devenv management

I'm using `poetry` because I'm used to it but it is entirely possible 
to generate a regular `pip`-like `requirements.txt` file within the CI 
pipeline and use `pip` to install dependencies, making the Docker image
even smaller.

Python dependencies: 
- [`fastapi`][fastapi]: API framework with built-in support for `pydantic` and `OpenAPI` spec
- [`jinja2`][jinja2]: lightweight templating engine
- [`aiofiles`][aiofiles]: async file I/O
- [`pydantic`][pydantic]: data validation and settings management using python type annotations

Containers: 
- [`docker`][docker] images, multi-stage builds for tests, dev and prod
- [`docker-compose`][docker-compose] stack deployment with files for dev and prod
- [`minikube`][minikube] local Kubernetes cluster for local testing

Testing:
- `pytest` for unit tests and test coverage
- [`behave`][behave] for behavioral tests
- [schemathesis][schemathesis] OpenAPI testing tool

# Data Types 

First let's get the initial idea of what the data types we're gonna be using
and what an api might look like.

```python
status: Enum = {
    "wip": "Contains any task or if any of its linked epics are wip",
    "pending_validation": "all tasks are done (removed) but Bugs are pending," +
                          "or any Epics are 'pending_validation'" +
                          "and no Epics are 'wip'",
    "completed": "there is no remaining tasks" +
                 "there is no remaining Bugs" +
                 "and all Epics are 'completed'",
    "blocked": "there are no remaining tasks" +
               "and there are remaining tasks in linked Epics"
}
```

# API

/v1/

- `DELETE /tasks/{task_id}` - should return the updated backlog 
                    with new status for Epics.
- `POST /tasks/` - create a new task

- `GET /bugs/` - list all Bugs and their corresponding [{epic_id}]
- `DELETE /bugs/{bug_id}` - should return the updated backlog with new 
                    status for Epics.

- `GET /epics` - lists all Epics in the current backlog and their status
- `POST /epics/{epic_id}` - add a new Task or Bug to {epic_id}
- `GET /epics/{epic_id}` - self explanatory

- `GET, POST /epics/{epic_id}/bugs` - list all Bugs from {epic_id} and linked Epics

- `GET /epics/blocked&{bug_id=BUG1}` - list all blocked Epics from a {bug_id}

- `GET /export` - return backlog as JSON


# Tests 

## Running the tests

3 steps of tests are available to run:

- `style_check`: isort, black, flake8
- `scan_vulnerabilities`: bandit, safety
- `tests`: mypy, pytest

callable with:  
`$ poetry run task {check_style, tests, scan_vulnerabilities}`


# Dev & Deployment

## Docker

**Requires `docker-compose` version 1.29.2 or higher**  
**Requires `docker` version 1.12 or higher**


`docker-compose` files are split into 3 parts: 

- `docker-compose.yml`: the main configuration file
- `docker-compose.override.yml`: the development configuration file
- `docker-compose.prod.yml`: the production configuration file

The main file defines services common to all environments.  
The development environment comes with a `mongo-express` service, 
that is used to monitor and browse the MongoDB server.  
The production environment comes with a `Traefik` service.
Trafik manages TLS and routing for our application.

### Development 

Standalone docker development environment in one command: 

`docker-compose up`  
*No need to specify the main or override file - they are automatically parsed*

This will spin up the following containers:

- `debian-mini-python39-backlog`
- `bitnami-mongodb`
- `mongo-express`

### Production

`docker-compose up -f docker-compose.yml -f docker-compose.prod.yml up -d`

This will spin up the following containers:

- `debian-mini-python39-backlog`
- `bitnami-mongodb`
- `traefik`

## Kubernetes

**Requires `kubectl` version 1.16.0 or higher**

Deploy to kubernetes cluster in one command:

`kubectl kustomize build k8s/overlays/development | kubectl apply -f -`


<!-- Links -->
[aiofiles]: https://aiofiles.readthedocs.io/en/stable/
[behave]: https://behave.readthedocs.io/en/latest/
[conventional-commits]: https://www.conventionalcommits.org/en/v1.0.0/
[docker]: https://www.docker.com/
[docker-compose]: https://docs.docker.com/compose/
[fastapi]: https://fastapi.tiangolo.com/
[minikube]: https://minikube.sigs.k8s.io/docs/start/
[jinja2]: https://jinja.palletsprojects.com/
[pydantic]: https://pydantic-docs.helpmanual.io/usage/
[pytest]: https://docs.pytest.org/en/7.1.x/contents.html
[schemathesis]: https://github.com/schemathesis/schemathesis
