from typing import Union

import pytest
from flask import Response
from flask_login import current_user

from backend.app.tests.conftest import CheckSplitterTestSuite


def assert_response(response: Response, status_code: int, json: Union[dict, str] = None):
    json = {} if not json else json
    assert response.status_code == status_code
    assert response.json == json


class TestRegisterSuite(CheckSplitterTestSuite):
    def test_register_user(self, get_model):
        """
        Тестирует успешную регистрацию пользователей

        :param get_model: фикстура для доступа к объекту из базы данных
        :return:
        """
        test_user_data = {
            "login": "PumPurum",
            "fullname": "Ivan Ivanych",
            "first_password": "QWErty1234",
            "second_password": "QWErty1234"
        }

        response = self.post(
            "app.auth.register_user",
            data=test_user_data
        )

        created_user = get_model("User", nickname=test_user_data["login"])

        assert created_user
        assert_response(response, 200, created_user.id)

    @pytest.mark.parametrize(
        "user_params, response_data",
        [
            pytest.param(
                {
                    "login": "PumPurum",
                    "fullname": "Ivan Ivanych",
                    "first_password": "QWErty1235",
                    "second_password": "QWErty1234"
                }
                , {"second_password": "Password mismatch"},
                id="Password missmatch",
            ),
            pytest.param(
                {
                    "login": "PumPurum",
                    "fullname": "Ivan Ivanych",
                    "first_password": "123456",
                    "second_password": "123456"
                }
                , {"first_password": "Password too simple"},
                id="Password too simple",
            ),
            pytest.param(
                {
                    "login": "user_for_tests_1",
                    "fullname": "Ivan Ivanych",
                    "first_password": "QWErty1235",
                    "second_password": "QWErty1235"
                }
                , {"login": "Login is already taken"},
                id="Login is already taken",
            )
        ]
    )
    def test_register_wrong_data(self, user_params, response_data, get_model, some_user):
        """
        Тестирует попытку регистрации с неправильными данными

        :param user_params: словарь с параметрами для создания пользователя
        :param response_data: словарь с данными, которые возвращает endpoint
        :param get_model: фикстура для доступа к объекту из базы данных
        :param some_user: фикстура для создания пользователя
        :return:
        """
        test_existing_user = some_user

        response = self.post(
            "app.auth.register_user",
            data=user_params
        )

        created_user = get_model("User", nickname=user_params["login"], fullname=user_params["fullname"])
        assert response.status_code == 403
        assert not created_user
        assert response.json == response_data


class TestLoginSuite(CheckSplitterTestSuite):
    def test_success_login(self, some_user):
        """
        Тестирует авторизацию

        :param some_user: фикстура для создания пользователя
        :return:
        """
        response = self.post(
            "app.auth.user_login",
            data={"login": some_user.nickname, "password": some_user.nickname}
        )

        assert_response(response=response, status_code=200, json="Login successfully")
        assert some_user == current_user
        assert current_user.is_authenticated

    @pytest.mark.parametrize(
        "user_params, response_data, status_code",
        [
            pytest.param(
                {}, 
                {"login": "field required", "password": "field required"}, 422, 
                id="Login with empty data"),
            pytest.param(
                {"login": "some_login", "password": "user_for_tests_1"},
                {"login": "User not found"}, 401,
                id="Login with wrong login"
            ),
            pytest.param(
                {"login": "user_for_tests_1", "password": "123456"},
                {'password': 'Wrong password'}, 401,
                id="Login with wrong password"
            )
        ]
    )
    def test_login_wrong_data(self, user_params, response_data, status_code, some_user):
        """
        Тестирует авторизацию пользователя с неправильными данными

        :param some_user: фикстура для создания пользователя
        :return:
        """
        response = self.post(
            "app.auth.user_login",
            data=user_params
        )

        assert_response(
            response=response,
            status_code=status_code,
            json=response_data
        )

    def test_login_already_logged_in(self, some_user):
        """
        Тестирует авторизацию уже авторизованного пользователя

        :param some_user: фикстура для создания пользователя
        :return:
        """
        self.post(
            "app.auth.user_login",
            data={"login": some_user.nickname, "password": some_user.nickname}
        )

        response = self.post(
            "app.auth.user_login",
            data={"login": some_user.nickname, "password": some_user.nickname}
        )

        assert_response(
            response=response,
            status_code=200,
            json="Already authorized"
        )
        assert current_user.is_authenticated

    def test_logged_out(self, some_user):
        """
        Тестирует выход из пользователя

        :param some_user: фикстура для создания пользователя
        :return:
        """
        self.post(
            "app.auth.user_login",
            data={"login": some_user.nickname, "password": some_user.nickname}
        )

        response = self.get(
            "app.auth.logout",
            data={"login": some_user.nickname, "password": some_user.nickname}
        )

        assert_response(
            response=response,
            status_code=200,
            json="Logout"
        )
        assert not current_user
