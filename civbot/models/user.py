from sqlalchemy import BigInteger, Column, String

from models.base_model import BaseModel


class User(BaseModel):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)
    steamId = Column(String)
    authkey = Column(String)
