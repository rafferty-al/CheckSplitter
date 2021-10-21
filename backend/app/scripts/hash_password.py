from pony import orm
from werkzeug.security import generate_password_hash

from backend.app.database.models import db
from backend.app.settings import settings

db.bind(
    provider=settings.PROVIDER,
    host=settings.HOST,
    port=settings.PORT,
    user=settings.USER,
    password=settings.PASSWORD,
    database=settings.DB_NAME,
)

orm.sql_debug(True)
db.generate_mapping(check_tables=True)


with orm.db_session:
    for user in db.User.select():
        user.password = generate_password_hash(user.password)
