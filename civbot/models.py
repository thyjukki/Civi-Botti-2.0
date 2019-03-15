from peewee import Proxy, Model, CharField, BigIntegerField, IntegerField, ForeignKeyField

database_proxy = Proxy()


class BaseModel(Model):
    class Meta:
        database = database_proxy


class User(BaseModel):
    id = BigIntegerField(primary_key=True)
    steam_id = CharField()
    authorization_key = CharField()


class Game(BaseModel):
    id = IntegerField(primary_key=True)
    owner = ForeignKeyField(User, backref='games')
    name = CharField()


class Subscription(BaseModel):
    game = ForeignKeyField(Game, backref='subscriptions')
    chat_id = BigIntegerField()
