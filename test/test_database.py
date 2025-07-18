
import os
import pytest
from unittest import mock
from GemTrack.data import database

@pytest.fixture
def temp_db_file(tmp_path, monkeypatch):
    test_db_file = tmp_path / "test.db"
    monkeypatch.setattr(database, "DB_FILE", str(test_db_file))
    return test_db_file

def test_ensure_assets_dir_creates_directory(tmp_path, monkeypatch):
    test_db_file = tmp_path / "test.db"
    monkeypatch.setattr(database, "DB_FILE", str(test_db_file))
    database.ensure_assets_dir()
    assert os.path.exists(tmp_path)

def test_db_file_exists_true(temp_db_file):
    temp_db_file.touch()
    assert database.db_file_exists() is True

def test_db_file_exists_false(temp_db_file):
    if temp_db_file.exists():
        temp_db_file.unlink()
    assert database.db_file_exists() is False

def test_check_db_file_accessible(temp_db_file):
    temp_db_file.write_text("test")
    # No debe lanzar excepción si el archivo es accesible
    try:
        database.check_db_file()
    except Exception as e:
        pytest.fail(f"Excepción inesperada: {e}")

def test_check_db_file_not_found(tmp_path, monkeypatch):
    test_db_file = tmp_path / "no_exists.db"
    monkeypatch.setattr(database, "DB_FILE", str(test_db_file))
    with pytest.raises(FileNotFoundError):
        database.check_db_file()

def test_check_db_file_no_permission(temp_db_file):
    temp_db_file.write_text("test")
    temp_db_file.chmod(0o000)
    try:
        with pytest.raises(PermissionError):
            database.check_db_file()
    finally:
        temp_db_file.chmod(0o600)  # Restaurar permisos para limpieza

def test_notify_db_status_exists(capsys, temp_db_file):
    database.notify_db_status(True)
    captured = capsys.readouterr()
    assert "ya existe" in captured.out

def test_notify_db_status_created(capsys, temp_db_file):
    database.notify_db_status(False)
    captured = capsys.readouterr()
    assert "Se ha creado" in captured.out

def test_init_db_calls_create_all(monkeypatch):
    mock_engine = mock.MagicMock()
    monkeypatch.setattr(database, "create_engine", lambda *a, **kw: mock_engine)
    mock_base = mock.MagicMock()
    monkeypatch.setattr(database, "Base", mock_base)
    database.init_db()
    assert mock_base.metadata.create_all.called

def test_setup_database_calls(monkeypatch):
    called = {"ensure": False, "exists": False, "init": False, "notify": False, "check": False}
    monkeypatch.setattr(database, "ensure_assets_dir", lambda: called.update({"ensure": True}))
    monkeypatch.setattr(database, "db_file_exists", lambda: called.update({"exists": True}) or False)
    monkeypatch.setattr(database, "init_db", lambda: called.update({"init": True}))
    monkeypatch.setattr(database, "notify_db_status", lambda exists: called.update({"notify": True}))
    monkeypatch.setattr(database, "check_db_file", lambda: called.update({"check": True}))
    database.setup_database()
    assert all(called.values())