from flask import request, url_for
from flask_login import current_user
from werkzeug.security import generate_password_hash

from app.tests.conftest import CheckSplitterTestSuite


class TestAuthSuite(CheckSplitterTestSuite):
    def test_user_login(self, app, create_model):
        test_user = create_model(
            "User",
            {
                "fullname": "test test",
                "nickname": "test1",
                "password": generate_password_hash("test1"),
            },
        )

        with app.test_client():
            response = self.post(
                "app.login",
                data={"nickname": "test1", "pwd": "test1"},
                follow_redirects=True,
            )

            assert response.status_code == 200
            assert response.request.path == url_for("app.index")
            assert test_user == current_user
