import pytest
from flask import url_for
from pony.orm import db_session, commit
from werkzeug.security import generate_password_hash

from app.database import models
from app.startup import db
from app.main import create_app


@pytest.fixture(scope="session")
def app():
    print("init app")
    app = create_app(testing=True)

    yield app


@pytest.fixture(autouse=True)
def clear_all_tables():
    db.create_tables(check_tables=True)
    yield
    db.drop_all_tables(with_all_data=True)


def _create_model(modelname: str, **kwargs):
    model_cls = getattr(models, modelname, None)
    model = model_cls(**kwargs)
    commit()
    return model


@pytest.fixture
def get_model():
    def _get_model(modelname: str, **kwargs):
        model_cls = getattr(models, modelname, None)
        model = model_cls.get(**kwargs)
        if model:
            return model

    with db_session:
        yield _get_model


@pytest.fixture()
def some_user():
    user_data = {
        "fullname": "test test",
        "nickname": "user_for_tests_1",
        "password": generate_password_hash("user_for_tests_1")
    }
    with db_session:
        created_user = _create_model("User", **user_data)

        yield created_user
        created_user.delete()


@pytest.fixture()
def another_user():
    user_data = {
        "fullname": "test test",
        "nickname": "user_for_tests_2",
        "password": generate_password_hash("user_for_tests_2")
    }
    with db_session:
        created_user = _create_model("User", **user_data)

        yield created_user

        created_user.delete()


@pytest.mark.usefixtures("client_class")
class CheckSplitterTestSuite:
    def _get_url(self, endpoint):
        return url_for(endpoint)

    def _get_headers(self, additional_headers=None, content_type="application/json"):
        headers = {"Content-Type": content_type}
        if additional_headers:
            headers.update(additional_headers)
        return headers

    def get(self, endpoint: str, **values):
        url = url_for(endpoint, **values)
        return self.client.get(url, headers=self._get_headers())

    def post(
        self,
        endpoint: str,
        data: dict = None,
        headers: dict = None,
        url_values: dict = None,
        use_json=True,
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
            )
        else:
            return self.client.post(
                url,
                data=data,
                headers=self._get_headers(headers, content_type="multipart/form-data"),
            )

    def patch(self, endpoint: str, json: dict):
        return self.client.patch(self._get_url(endpoint), json=json, headers=self._get_headers())

    def delete(self, endpoint: str, json: dict):
        return self.client.delete(self._get_url(endpoint), json=json, headers=self._get_headers())

