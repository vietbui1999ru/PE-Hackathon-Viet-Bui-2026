from app.database import require_env
import pytest

"""
Function to test and assert against environment database name.
Testing app.database's require_env function:
1. monkey patch creates fake environment,
2. use require_env from app.database to fetch from map database_name
3. compare against monkeypatch's test_db name. 
Expect to return success and true.

monkeypatch : pytest fixture built-in tool
"""
def test_env_success(monkeypatch):
    monkeypatch.setenv("DATABASE_NAME", "test_db")
    assert require_env("DATABASE_NAME") == "test_db"

"""
Function to test and fail against environment database name.
Testing app.database's require_env function:
1. monkey patch deletes fake environment (empty environment),
2. use require_env from app.database to fetch from map database_name
3. compare against monkeypatch's empty environment, raising=False expect us to fail silently ignore if environment doesn't exist (make sure env's not there). 
Expect to return False Raise Error and issue of missing environment.

monkeypatch : pytest fixture built-in tool
"""
def test_env_missing(monkeypatch):
    monkeypatch.delenv("DATABASE_NAME", raising=False)

    # test expected failures. Code must raise rntime error (true negatives). else test fails (false negatives)
    with pytest.raises(RuntimeError):
        require_env("DATABASE_NAME")
