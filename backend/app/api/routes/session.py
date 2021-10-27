from collections import defaultdict
from datetime import datetime

from flask import Blueprint, request
from flask_login import login_required


from app.api.helpers.session import get_orders_data, debt_calc
from app.api.helpers.utils import error, success
from app.schemas.session import (
    UserSchema,
    SessionResponseSchema,
    SessionUpdateRequestSchema,
    UserInSessionSchema
)
from backend.app.startup import db


session_blueprint = Blueprint("session", __name__, url_prefix="/session")


@session_blueprint.route("/<int:sid>")
@login_required
def session_info(sid):
    session = db.Session.get(id=sid)
    if session is None:
        return error(status_code=404, description="Session not found")

    users = [UserSchema.from_orm(uis.user) for uis in session.users.order_by(lambda u: u.id)[:]]

    # all orders in session
    orders = get_orders_data(session)

    session_schema = SessionResponseSchema(
        order_items=orders,
        user_items=users,
        start=session.start,
        end=session.end,
        title=session.title
    )
    return success(session_schema.json())


@session_blueprint.route("/<int:sid>", methods=["POST"])
@login_required
def update_session(sid):
    session = db.Session.get(id=sid)
    if session is None:
        return error(status_code=404, description="Session not found")

    session_form = SessionUpdateRequestSchema(**request.json)
    if session_form.title:
        session.title = session_form.title

    if session_form.end_session:
        user_debts = defaultdict(int)

        # users summary paid for debt
        maintainers = [UserInSessionSchema(**uis.user) for uis in session.users]

        # orders and users in orders for session
        orders = get_orders_data(session)

        for order in orders:
            count = len(order.users)
            for user in order.users:
                user_debts[user.name] += order.price / count

        should_be = sum(order.price for order in orders)
        maintained = sum(maintainer.value for maintainer in maintainers)
        if should_be <= maintained:
            # TODO conditions when impossible to end the session
            session.end = datetime.now()
            debt_calc(session, maintainers, user_debts)
            return success("Session was end")
        else:
            return error(status_code=500, description="Not enough money for paid debt")
    return success("Successfully updated")
