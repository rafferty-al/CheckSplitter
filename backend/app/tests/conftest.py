import pytest
from flask import url_for
from flask_login import login_user, logout_user
from pony.orm import db_session, commit
from werkzeug.security import generate_password_hash
from random import randint

from app.database import models
from app.main import create_app


@pytest.fixture(scope="session")
def app(request):
    print("init app")
    app = create_app(testing=True)

    yield app


@pytest.fixture
def create_model():
    def _create_model(modelname: str, data: dict):
        model_cls = getattr(models, modelname, None)
        model = model_cls(**data)
        commit()
        return model

    with db_session:
        yield _create_model


@pytest.fixture
def get_model():
    def _get_model(modelname: str, data: dict):
        model_cls = getattr(models, modelname, None)
        model = model_cls.get(**data)
        if model:
            return model
        else:
            raise AttributeError("This model does not exists")

    with db_session:
        yield _get_model


@pytest.fixture
def login():
    def _login(user: models.User):
        login_user(user)

    yield _login
    logout_user()


@pytest.fixture
def create_user():
    def _create_user(nickname=f"test{randint(0, 100)}"):
        model_cls = getattr(models, "User", None)
        data = {
            "nickname": nickname,
            "fullname": nickname + "test1",
            "password": generate_password_hash(nickname)
        }
        model = model_cls(**data)
        commit()
        return model

    with db_session:
        yield _create_user


@pytest.mark.usefixtures("client_class")
class CheckSplitterTestSuite:
    def _get_headers(self, additional_headers=None, content_type="application/json"):
        headers = {"Content-Type": content_type}
        if additional_headers is not None:
            headers.update(additional_headers)
        return headers

    def get(self, endpoint: str, follow_redirects=True, **values):
        url = url_for(endpoint, **values)
        return self.client.get(url, headers=self._get_headers(), follow_redirects=follow_redirects)

    def post(
        self,
        endpoint: str,
        data: dict = None,
        headers: dict = None,
        url_values: dict = None,
        use_json=False,
        follow_redirects=False,
    ):
        if not data:
            data = {}
        if url_values is not None:
            url = url_for(endpoint, **url_values)
        else:
            url = url_for(endpoint)
        if use_json:
            return self.client.post(
                url,
                json=data,
                headers=self._get_headers(headers, content_type="application/json"),
                follow_redirects=follow_redirects,
            )
        else:
            return self.client.post(
                url,
                data=data,
                headers=self._get_headers(headers, content_type="multipart/form-data"),
                follow_redirects=follow_redirects,
            )

    def patch(self, endpoint: str, json: dict):
        url = url_for(endpoint)
        return self.client.patch(url, json=json, headers=self._get_headers())

    def delete(self, endpoint: str, json: dict):
        url = url_for(endpoint)
        return self.client.delete(url, json=json, headers=self._get_headers())
