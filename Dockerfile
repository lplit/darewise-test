# `python-base` sets up all our shared environment variables
FROM python:3.9-slim as python-base

ENV PYTHONUNBUFFERED=1                  \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1           \
    # pip
    PIP_NO_CACHE_DIR=off                \
    PIP_DISABLE_PIP_VERSION_CHECK=on    \
    PIP_DEFAULT_TIMEOUT=100             \
    # poetry
    POETRY_HOME="/opt/poetry"           \
    POETRY_VIRTUALENVS_IN_PROJECT=true  \
    POETRY_NO_INTERACTION=1             \
    # paths where requirements + virtual environment will live
    PYSETUP_PATH="/opt/pysetup"         \
    VENV_PATH="/opt/pysetup/.venv"      \
    PYTHONPATH="/app/src/" 
# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"


# `builder-base` stage is used to build deps + create our virtual environment
FROM python-base as builder-base
RUN apt-get update                                \
    && apt-get install --no-install-recommends -y \
    curl                                          \
    build-essential                               \ 
    && rm -rf /var/lib/apt/lists/*
# install poetry - respects $POETRY_HOME
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./
# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install --no-dev


# `development` image is used during development / testing
FROM python-base as development
WORKDIR $PYSETUP_PATH
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY ./ /app/
RUN poetry install
WORKDIR /app 
ENTRYPOINT [ "/app/src/entrypoint.sh" ]


# `production` image used for runtime
FROM python-base as production
ENV PYTHONPATH=/app/src/
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY . /app
WORKDIR /app/src
CMD [ "/app/src/entrypoint.sh" ]

