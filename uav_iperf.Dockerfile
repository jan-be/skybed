# modified from https://stackoverflow.com/questions/53835198/integrating-python-poetry-with-docker?answertab=trending#tab-top

FROM python:3.13-slim

RUN apt update && apt install -y curl gcc iperf3

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # Poetry's configuration:
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local' \
  POETRY_VERSION=1.8.4

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /code
COPY . /code

# Project initialization:
RUN poetry install --no-interaction --no-ansi

CMD uav