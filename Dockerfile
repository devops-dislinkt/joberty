FROM python:3.10-slim-buster
WORKDIR /code
RUN pip install poetry
RUN pip install flask_cors
COPY ./poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.create false
RUN poetry install
EXPOSE 8001
WORKDIR /code/app
ENTRYPOINT ["poetry", "run", "python", "run.py"]