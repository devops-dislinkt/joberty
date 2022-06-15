import os

user = (
    os.environ["DATABASE_USERNAME"] if "DATABASE_USERNAME" in os.environ else "postgres"
)
password = (
    os.environ["DATABASE_PASSWORD"] if "DATABASE_USERNAME" in os.environ else "postgres"
)
host = os.environ["DATABASE_DOMAIN"] if "DATABASE_DOMAIN" in os.environ else "localhost"
database = (
    os.environ["DATABASE_SCHEMA"] if "DATABASE_SCHEMA" in os.environ else "postgres"
)
port = os.environ["DATABASE_PORT"] if "DATABASE_PORT" in os.environ else 5432
secret_key = (
    os.environ["FLASK_SECRET_KEY"] if "FLASK_SECRET_KEY" in os.environ else "secret"
)

DATABASE_CONNECTION_URI = (
    f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
)

KAFKA_1 = os.environ["KAFKA1"] if "KAFKA" in os.environ else "none"
KAFKA_TOPIC = (
    os.environ["KAFKA_TOPIC"] if "KAFKA_TOPIC" in os.environ else "default-topic"
)
