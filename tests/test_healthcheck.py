from __future__ import annotations

from flask import Flask
import pytest

from app import create_app


@pytest.fixture
def app() -> Flask:
    return create_app({"TESTING": True})


@pytest.fixture
def client(app: Flask):
    return app.test_client()


def test_healthcheck(client) -> None:
    res = client.get("/health")
    assert res.status_code == 200
    assert res.data.decode() == "ok"
