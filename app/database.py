import os

from peewee import DatabaseProxy, Model, PostgresqlDatabase, SqliteDatabase

db = DatabaseProxy()


class BaseModel(Model):
    class Meta:
        database = db

"""
Function to request user to provide environment variables,
not dependent on default values for security reasons.
Input : environment : str
Return : variables : str
"""
def require_env(environment : str) -> str:
    variables = os.environ.get(environment)
    if variables is None or variables.strip() == "":
        raise RuntimeError(f"Missing required environment variable: {environment}")
    return variables

def init_db(app):
    db_name = os.environ.get("DATABASE_NAME")
    db_user = os.environ.get("DATABASE_USER")
    db_password = os.environ.get("DATABASE_PASSWORD")
    db_host = os.environ.get("DATABASE_HOST", "localhost")
    db_port = int(os.environ.get("DATABASE_PORT", 5432))

    if db_name and db_user and db_password:
        database = PostgresqlDatabase(
            db_name,
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
        )
        app.config["DB_BACKEND"] = "postgres"
    else:
        database = SqliteDatabase("local_dev.db")
        app.config["DB_BACKEND"] = "sqlite"

    db.initialize(database)

    @app.before_request
    def _db_connect():
        db.connect(reuse_if_open=True)

    @app.teardown_appcontext
    def _db_close(exc):
        if not db.is_closed():
            db.close()
