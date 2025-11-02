from peewee import PostgresqlDatabase, Model, TextField, TimestampField

import my_secrets

db = PostgresqlDatabase(my_secrets.DATABASE_INFO["type_name"],
                        user=my_secrets.DATABASE_INFO["user"],
                        password=my_secrets.DATABASE_INFO["password"],
                        host=my_secrets.DATABASE_INFO["host"],
                        port=my_secrets.DATABASE_INFO["port"])


class WatchListRecord(Model):
    type_name = TextField(choices=['anime', 'film', 'tv-show'])
    information_url = TextField(unique=True)
    creator = TextField()
    note = TextField(null=True)

    status = TextField(choices=["added", "scheduled", "watched"])
    created_at = TimestampField()
    watched_at = TimestampField(null=True)

    class Meta:
        database = db

# db.drop_tables([WatchListRecord])
# db.create_tables([WatchListRecord])
