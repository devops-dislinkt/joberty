FROM python:3.10-slim-buster
WORKDIR /code
RUN pip install poetry
COPY . .
RUN poetry config virtualenvs.create false
RUN poetry config virtualenvs.in-project true
RUN poetry install
EXPOSE 8001
WORKDIR /code/app
CMD poetry run python run.py 8001