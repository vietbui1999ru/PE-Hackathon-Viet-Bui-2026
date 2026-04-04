import os

from peewee import DatabaseProxy, Model, PostgresqlDatabase

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
        raise RuntimeError(f"Missing required environment variables: {environment}")
    return variables

def init_db(app):

    database = PostgresqlDatabase(
            # require environment wth db_name
            require_env("DATABASE_NAME"),
            # allow  change of host, defaults to localhost
            host=os.environ.get("DATABASE_HOST", "localhost"),
            # allow change of port, defaults to 5432
            port=int(os.environ.get("DATABASE_PORT", 5432)),
            # require environment wth db_user
            user=require_env("DATABASE_USER"),
            # require environment wth db_password DO NOT EXPOSE.
            password=require_env("DATABASE_PASSWORD"),
    )
    db.initialize(database)

    @app.before_request
    def _db_connect():
        db.connect(reuse_if_open=True)

    @app.teardown_appcontext
    def _db_close(exc):
        if not db.is_closed():
            db.close()
