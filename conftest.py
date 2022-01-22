import datetime
from datetime import date as date_type
from datetime import datetime as datetime_type
from decimal import Decimal

import pytest

from core.db_primitives import CoreField, CoreModel
from orms_tools import (
    DjangoModelPrinter,
    DjangoModulePrinter,
    DjangoOrmModelCombine,
    SQLAlchemyModelCombine,
    SqlAlchemyModelPrinter,
    SqlAlchemyModulePrinter,
)


class SaSetupFixture:
    combine = SQLAlchemyModelCombine
    model_printer = SqlAlchemyModelPrinter
    module_printer = SqlAlchemyModulePrinter


class DjangoSetupFixture:
    combine = DjangoOrmModelCombine
    model_printer = DjangoModelPrinter
    module_printer = DjangoModulePrinter


user_core_model = CoreModel(
    doc="""Some User Model""",
    tablename="user",
    unique_together=(("level", "coeff"),),
    fields=[
        CoreField(
            sql_type=int,
            name="id",
            doc="UserId",
            primary_key=True,
        ),
        CoreField(
            sql_type=int,
            name="level",
            doc="User level",
        ),
        CoreField(
            sql_type=str,
            name="nickname",
            doc="Nickname",
            length=32,
            unique=True,
        ),
        CoreField(
            sql_type=bool,
            name="is_active",
            default=True,
        ),
        CoreField(sql_type=float, name="coeff", precision=8, default=1.1),
        CoreField(
            sql_type=datetime_type, name="reg_time", auto_on_create=True,
        ),
        CoreField(
            sql_type=date_type, name="birthday", auto_on_create=True, auto_on_update=True,
        ),
        CoreField(
            sql_type=bytes,
            name="signature",
            nullable=False,
            default=b"1010",
            length=4,
        ),
        CoreField(sql_type=Decimal, name="balance", precision=2, scale=10),
    ],
)

payment_core_model = CoreModel(
    doc="""Some Payment""",
    tablename="payment",
    fields=[
        CoreField(
            sql_type=int,
            name="id",
            doc="UserId",
            primary_key=True,
        ),
        CoreField(
            sql_type=Decimal,
            name="payment",
        ),
        CoreField(
            sql_type=int,
            name="user_id",
            doc="UserId",
            foreign_key="User.id",
            nullable=False,
        ),
    ],
)
