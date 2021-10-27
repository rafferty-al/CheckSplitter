from datetime import datetime

from flask_login import login_user
from pony.orm import db_session
from werkzeug.security import generate_password_hash

from app.tests.conftest import CheckSplitterTestSuite, _create_model


class TestSessionSuite(CheckSplitterTestSuite):
    def test_session_get(self, some_user):
        self.post(
            "app.auth.user_login",
            data={"login": some_user.nickname, "password": some_user.nickname}
        )
        with db_session:
            session = _create_model("Session", title="Test session name", start=datetime.now())
            created_users = [
                _create_model(
                    "User",
                    nickname=f"user_for_tests_{i}",
                    password=generate_password_hash(f"users_for_tests"),
                    fullname=f"test test {i}",
                )
                for i in range(2, 7)
            ]
            uis = []
            orders = []
            for user in created_users:
                uis_model = _create_model("UserInSession", value=0, session=session, user=user)
                order_model = _create_model(
                    "OrderedItem",
                    title="order" + user.fullname,
                    price=333,
                    user_in_sessions=uis_model,
                    session=session)
                user.sessions = uis_model
                uis.append(uis_model)
                orders.append(order_model)

        response = self.get("app.session.session_info", sid=session.id)

        assert response.status_code == 200

