from app.database.models import db


def debt_calc(session, maintainers, users_dict, values):
    slaves = []
    masters = []

    for k, v in maintainers.items():
        name = users_dict[k]
        ordered = values[name]
        val = int(v - ordered)
        if val < 0:
            slaves.append((-val, name))
        else:
            masters.append((val, name))

    masters.sort(key=lambda i: i[0], reverse=True)
    slaves.sort(key=lambda i: i[0], reverse=True)

    if slaves and masters:
        log = []
        s_val, slave = slaves.pop(0)
        m_val, master = masters.pop(0)
        while slave:
            if m_val > s_val:
                log.append((slave, master, s_val))
                m_val -= s_val
                if len(slaves) > 0:
                    s_val, slave = slaves.pop(0)
                else:
                    break
            elif s_val > m_val:
                log.append((slave, master, m_val))
                s_val -= m_val
                if len(masters) > 0:
                    m_val, master = masters.pop(0)
                else:
                    break
            else:
                log.append((slave, master, s_val))
                if len(slaves) > 0:
                    s_val, slave = slaves.pop(0)
                else:
                    break
                if len(masters) > 0:
                    m_val, master = masters.pop(0)
                else:
                    break
        # TODO Checkout different variants of ending a session
        for debt in log:
            m = db.User[debt[1]]
            s = db.User[debt[0]]
            c = db.Credit.get(master=m, slave=s)
            if c is not None:
                c.value += debt[2]
            else:
                db.Credit(master=m, slave=s, value=debt[2])