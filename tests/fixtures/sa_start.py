import sqlalchemy as sa
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta
import datetime

metadata = sa.MetaData()
Base: DeclarativeMeta = declarative_base(metadata=metadata)


class User(Base):
    """Some User Table."""

    __tablename__ = 'user'

    __table_args__ = (
        sa.UniqueConstraint('level', 'coeff'),
    )

    id = sa.Column(sa.Integer, primary_key=True, doc='UserID')
    level = sa.Column(sa.Integer, doc='User level', default=1)
    nickname = sa.Column(sa.String, unique=True, doc="Nickname")
    is_active = sa.Column(sa.Boolean, default=True)
    coeff = sa.Column(sa.Float, default=1.1)
    signature = sa.Column(sa.BINARY, default=b'0101', nullable=False)
    reg_time = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    birthday = sa.Column(sa.Date, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    balance = sa.Column(sa.DECIMAL(2, 10))


class Payment(Base):
    __tablename__ = "payment"

    id = sa.Column(sa.Integer, primary_key=True)
    sum = sa.Column(sa.DECIMAL)
    user_id = sa.Column(sa.Integer, sa.ForeignKey(User.id), nullable=False, doc='Payed by user')
