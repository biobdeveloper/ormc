import sqlalchemy as sa
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta

metadata = sa.MetaData()

SABase: DeclarativeMeta = declarative_base(metadata=metadata)
