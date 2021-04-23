from pony import orm

from backend.app.database.models import db
from backend.app.settings import settings

db.bind(provider=settings.PROVIDER,
        host=settings.HOST,
        port=settings.PORT,
        user=settings.USER,
        password=settings.PASSWORD,
        database=settings.DB_NAME)

orm.sql_debug(True)
db.generate_mapping(check_tables=True)


with orm.db_session:
    for i in range(10):
        user = db.User(fullname=f'Test User №{i}', password='123456', nickname=f'test{i}')
        print(f'User number {i} was created')
