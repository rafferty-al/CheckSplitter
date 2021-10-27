from app.schemas.session import OrderSchema, UserSchema, UserInSessionSchema, LogSchema
from backend.app.startup import db


def get_orders_data(session: db.Session) -> list:
    orders = []
    for order in session.orders:
        # users, included in this order
        users_in_order = []
        for uis in order.user_in_sessions:
            users_in_order.append(UserSchema.from_orm(uis.user))
        orders.append(OrderSchema(title=order.title, price=order.price, users=users_in_order))
    return orders


def debt_calc(session: db.Session, maintainers: list, piece_of_debt: dict):
    slaves = []
    masters = []

    for maintainer in maintainers:
        ordered = piece_of_debt[maintainer.nickname]
        contribution = int(maintainer.contribution - ordered)
        if contribution < 0:
            slaves.append(UserInSessionSchema(value=-contribution, **maintainer))
        else:
            masters.append(UserInSessionSchema(value=contribution, **maintainer))

    masters.sort(key=lambda uis: uis.value, reverse=True)
    slaves.sort(key=lambda uis: uis.value, reverse=True)

    if slaves and masters:
        log = []
        slave = slaves.pop(0)
        master = masters.pop(0)
        # пока есть должники бежим по кредиторам и пытаемся покрыть его должником
        # при полном закрытии долга кредитору переходим к след. должнику, пока не кончатся
        while slave:
            if master.value > slave.value:
                log.append(LogSchema(debtor=slave, creditor=master, value=slave.value))
                master.value -= slave.value
                if len(slaves) > 0:
                    slave = slaves.pop(0)
                else:
                    break
            elif slave.value > master.value:
                log.append(LogSchema(debtor=slave, creditor=master, value=master.value))
                slave.value -= master.value
                if len(masters) > 0:
                    master = masters.pop(0)
                else:
                    break
            else:
                log.append(LogSchema(debtor=slave, creditor=master, value=slave.value))
                if len(slaves) > 0:
                    slave.value, slave = slaves.pop(0)
                elif len(masters) > 0:
                    master = masters.pop(0)
                else:
                    break
        # TODO Checkout different variants of ending a session
        for log_write in log:
            m = db.User[log_write.creditor.id]
            s = db.User[log_write.debtor.id]
            c = db.Credit.get(master=m, slave=s)
            if c is not None:
                c.value += log_write.value
            else:
                db.Credit(master=m, slave=s, value=log_write.value)
