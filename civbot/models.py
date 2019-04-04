from steamwebapi import profiles
from peewee import Proxy, Model, CharField, BigIntegerField, IntegerField, \
    ForeignKeyField, BooleanField

from civbot import gmr

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

    def ongoing(self):
        games = gmr.get_games(
            self.id,
            self.owner.steam_id
        )
        return len([g for g in games if g['GameId'] == self.id]) == 1


class Player(BaseModel):
    steam_id = BigIntegerField()
    game = ForeignKeyField(Game, backref='players')
    order = IntegerField()

    def registered_user(self):
        return User.get_or_none(User.steam_id == self.steam_id)

    def get_name(self, bot):
        user = self.registered_user()
        if user:
            return bot.get_chat(user.id).username
        user_profile = profiles.get_user_profile(f'{self.steam_id}')
        return user_profile.personaname


class Subscription(BaseModel):
    game = ForeignKeyField(Game, backref='subscriptions')
    chat_id = BigIntegerField()
