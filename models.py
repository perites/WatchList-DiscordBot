from peewee import PostgresqlDatabase, Model, TextField, TimestampField, IntegerField

import secrets

db = PostgresqlDatabase(secrets.DATABASE_INFO["name"],
                        user=secrets.DATABASE_INFO["user"],
                        password=secrets.DATABASE_INFO["password"],
                        host=secrets.DATABASE_INFO["host"],
                        port=secrets.DATABASE_INFO["port"])


class WatchListEntity(Model):
    info_link = TextField(unique=True)
    type = TextField(choices=['anime', 'film', 'tv-show'])
    status = IntegerField()
    creator = TextField()
    note = TextField(null=True)
    created_at = TimestampField()

    class Meta:
        database = db


db.connect()

# print(list((WatchListEntity.select())))
#
# db.drop_tables([WatchListEntity])
# db.create_tables([WatchListEntity])
