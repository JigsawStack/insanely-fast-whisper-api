FROM nvcr.io/nvidia/pytorch:24.01-py3

ENV PYTHON_VERSION=3.10
ENV POETRY_VENV=/app/.venv

RUN apt-get update && apt-get install -y --no-install-recommends \
    python${PYTHON_VERSION}-venv \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN python -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==1.7.1

ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /app

COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.in-project true
RUN poetry install --no-root

COPY . .

RUN poetry install
RUN $POETRY_VENV/bin/pip install -U wheel \
    && $POETRY_VENV/bin/pip install ninja packaging

RUN $POETRY_VENV/bin/pip install flash-attn --no-build-isolation

EXPOSE 9000

CMD gunicorn --bind 0.0.0.0:9000 --workers 1 --timeout 0 app.app:app -k uvicorn.workers.UvicornWorker