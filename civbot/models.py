from peewee import Proxy, Model, CharField, BigIntegerField

database_proxy = Proxy()


class BaseModel(Model):
    class Meta:
        database = database_proxy


class User(BaseModel):
    id = BigIntegerField(primary_key=True)
    steam_id = CharField()
    authorization_key = CharField()
