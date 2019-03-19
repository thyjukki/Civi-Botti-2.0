import telegram
from peewee import Proxy, Model, CharField, BigIntegerField, IntegerField, \
    ForeignKeyField, BooleanField

database_proxy = Proxy()


class BaseModel(Model):
    class Meta:
        database = database_proxy

    def refresh(self):
        return type(self).get(self._pk_expr())


class User(BaseModel):
    id = BigIntegerField(primary_key=True)
    steam_id = BigIntegerField()
    authorization_key = CharField()

class Game(BaseModel):

    id = IntegerField(primary_key=True)
    owner = ForeignKeyField(User, backref='games')
    name = CharField()
    active = BooleanField(default=True)
    current_steam_id = BigIntegerField(null=True)


class Subscription(BaseModel):
    game = ForeignKeyField(Game, backref='subscriptions')
    chat_id = BigIntegerField()
