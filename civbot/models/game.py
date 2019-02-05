from sqlalchemy import Column, ForeignKey, BigInteger, String, Boolean
from sqlalchemy.orm import relationship

from civbot.models.base_model import BaseModel


class Game(BaseModel):
    __tablename__ = 'games'
    gameId = Column(BigInteger, primary_key=True)
    ownerId = Column(BigInteger, ForeignKey("user.id"))
    owner = relationship("User")
    name = Column(String)
    currentTp = Column(String)
    notified = Column(Boolean)
    turnId = Column(String)
