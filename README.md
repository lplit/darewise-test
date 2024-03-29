Backlog tracking tool

# Repository

Backlog tracking tool is a home assignment test project written for 
[DareWise][darewise] for Python Developer position.

Assignment Assumptions: 
- Backlog Keys, i.e. "EpicA", "EpicB", etc. are unique, as this is a dictionary. 
- Backlog is properly formatted, i.e. 
  - No circular references
  - Tasks and bugs are always assigned to an Epic (no free agents)

The repository follows [Conventional Commits][conventional-commits] 
and uses.


## Stack

DevEnv tools:
- `poetry`: dependency & devenv management

Python tools: 
- [`black`][black]: Uncompromising Python code formatter 
- [`isort`][isort]: Library to sort imports
- [`flake8`][flake8]: Style guide Enforcement
- [`mypy`][mypy]: Optional static type checker for Python
- [`pytest`][pytest]: Framework to write small, readable tests
- [`poetry`][poetry]: Dependency & devenv management

I'm using `poetry` because I'm used to it but it is entirely possible 
to generate a regular `pip`-like `requirements.txt` file within the CI 
pipeline (or docker) and use `pip` to install dependencies, making 
the Docker image even smaller (currently ~520mb uncompressed).

Python dependencies: 
- [`fastapi`][fastapi]: API framework with built-in support for `pydantic` and `OpenAPI` spec
- [`mongoengine`][mongoengine]: Document-Object Mapper (think ORM, but for document databases) 
    for working with MongoDB from Python
- [`pydantic`][pydantic]: data validation and settings management using python type annotations

Containers: 
- [`docker`][docker] images, multi-stage builds for tests, dev and prod
- [`docker-compose`][docker-compose] stack deployment with files for dev and prod
- [`minikube`][minikube] local Kubernetes cluster for testing

Testing:
- [`pytest`][pytest] for unit tests and test coverage
- [`behave`][behave] for behavioral tests
- [schemathesis][schemathesis] OpenAPI testing tool


# API

FastAPI supports the [OpenAPI specification][oas], which is automatically
visualized with either SwaggerUI or Redoc, full API specifications
with models etc, are available at:

- `localhost:8000/docs` for SwaggerUI
- `localhost:8000/redoc` for Redoc

High level API architecture:

- [x] `GET /v1/backlog` - Get the backlog
- [x] `POST /v1/backlog` - Parse a backlog, merge if already existing

- [x] `GET /v1/epics` - Get all epics and their status
- [x] `POST /v1/epics/{epic_id}` - Add a task or a bug to epic. Returns backlog.
- [x] `GET /v1/epics/{epic_id}/bugs` - Return all Bugs and all linked Epics' bugs
- [ ] `GET /v1/epics/blocked` - Get all blocked Epics.

- [x] `DELETE /v1/tasks/{task_id}` - Remove a task from backlog. Returns updated backlog
- [x] `DELETE /v1/bugs/{bug_id}` - Remove a bug from backlog. Returns updated backlog

# Dev & Deployment

## Docker

**Requires `docker-compose` version 1.29.2 or higher**  
**Requires `docker` version 1.12 or higher**


- `docker-compose.yml`: the main configuration file


The main file defines services common to all environments.  
The development environment comes with a `mongo-express` service, 
that is used to monitor and browse the MongoDB server.

Standalone docker development environment in one command: 

`docker-compose up`  

This will spin up the following containers:

- `backlog`
- `bitnami-mongodb`
- `mongo-express`

## Kubernetes

**Requires `kubectl` version 1.14 or higher**

Using [kustomize][kustomize] to generate kube files. 
The deployment is split in two main parts: 
- [`/k8s/base/`](./k8s/base/) with the building blocks for deployments
- [`/k8s/overlays/{development, staging, production}`](./k8s/overlays/) with the 
  specific configuration for each environment

NOTE: Staging and production environments are not implemented.

Deploy to kubernetes cluster in one command:

`kubectl kustomize build k8s/overlays/development | kubectl apply -f -`

### minikube

Steps to get it working on minikube

```bash
$[1] minikube start --driver=docker --disk-size 30GB --cpus 12 --memory 16000 --addons dashboard --addons metrics-server
$[1] minikube image build -t backlog:latest .
$[1] kubectl kustomize build k8s/overlays/development | kubectl apply -f -
# In a new terminal, let it live
$[2] minikube tunnel 
$[1] minikube service backlog --url
```
and browse to the url provided by the last command.

## Tests 

### Running the tests

3 steps of tests are available to run:

- `style_check`: isort, black, flake8
- `scan_vulnerabilities`: bandit, safety
- `tests`: mypy, pytest

callable with:  
`$ poetry run task {check_style, tests, scan_vulnerabilities}`

`tests` **MUST** be ran from within the docker container, as such: 

`$ docker exec darewise-test_backlog_1 poetry run task check_style`

with `darewise-test_backlog_1` being the container name. The reason behind 
is the lack of envars needed to spin up the service.

# Next steps

## General

- Implementing specific collections for Tasks and Bugs would be the first step, as they're
just barely strings for now. 

- Although Reference links for Epics are implemented, it would be necessary to do the same 
for Tasks and Bugs.

- Streamlining the Pydantic Models for input/output would be a good idea.

- The endpoint to list all *Blocked* Epics was not implemented because the spec given was
  identical to *Work In Progress* and there were many other things to do.

- Depending on the target environment, if using `docker-compose`, we could split 
  up `docker-compose.yaml` into three files: 
    - `docker-compose.yaml`: the main configuration file
    - `docker-compose.override.yaml`: development or staging environment
    - `docker-compose.prod.yaml`: staging or production environment

- For k8s deployments, we could write a helm chart.
- For k8s, secrets management is currently inexistent
- Add kubernetes liveness and readiness probes
  
## Testing

For the sake of this test only very rudimentary testing was implemented.  
Proper testing should be implemented, with sequential/behavioral tests: create>verify>delete>verify.  
Those were done manually for the sake of this test, but should be implemented. It could
be achieved with Cucumber syntax, using [Behave][behave] for example, or vanilla [pytest][pytest].

Adding the Poetry testing tasks to the CI pipeline, or docker stages to automate the testing 
would be beneficial.

Input sanitization is not implemented at all. This leads to *schemathesis* being able 
to post garbage into the database:
```json
{
    _id: ObjectId('625daad14dfd9b8252c16887'),
    epic_id: '¿ýé\u0083񀃭a)',
    Tasks: [
        '',
        '¸􌉡½÷',
        '\u0019=\f\u009aq',
        '\u001a\u0081õ',
        'k'
    ],
    Bugs: [
        '\u001a󌜤æT𷞔\u000b¥񴠇\u0094<𠛇',
        '&à',
        'WÒ蚅c',
        '\u000f󸒎x~',
        'w2z',
        '\u0086-Z'
    ],
    Epics: []
}
```




<!-- Links -->
[aiofiles]: https://aiofiles.readthedocs.io/en/stable/
[behave]: https://behave.readthedocs.io/en/latest/
[black]: https://black.readthedocs.io/en/stable/
[conventional-commits]: https://www.conventionalcommits.org/en/v1.0.0/
[docker]: https://www.docker.com/
[docker-compose]: https://docs.docker.com/compose/
[fastapi]: https://fastapi.tiangolo.com/
[flake8]: https://flake8.pycqa.org/en/latest/
[isort]: https://pycqa.github.io/isort/
[jinja2]: https://jinja.palletsprojects.com/
[kustomize]: https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/
[minikube]: https://minikube.sigs.k8s.io/docs/start/
[mongoengine]: http://mongoengine.org/
[mypy]: https://mypy.readthedocs.io/en/stable/
[oas]: https://swagger.io/specification/
[poetry]: https://python-poetry.org/
[pydantic]: https://pydantic-docs.helpmanual.io/usage/
[pytest]: https://docs.pytest.org/en/7.1.x/contents.html
[schemathesis]: https://github.com/schemathesis/schemathesis
