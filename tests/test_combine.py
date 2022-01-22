import datetime
import decimal

import sqlalchemy as sa
from django.db import models as dm

from conftest import (
    payment_core_model,
    user_core_model,
)
from core.utils import import_user_module
from orms_tools import DjangoOrmModelCombine, SQLAlchemyModelCombine

sa_combine = SQLAlchemyModelCombine()
django_combine = DjangoOrmModelCombine()

with open('fixtures/sa_start.py') as f:
    sa_example_text = f.read()

with open('fixtures/django_start.py') as f:
    djangoorm_example_text = f.read()


def test_import_sa_user_module():
    user_module = import_user_module(sa_example_text)
    assert user_module.User


def test_import_djangoorm_user_module():
    user_module = import_user_module(djangoorm_example_text)
    assert user_module.User


def test_retrieve_sa_models_from_module():
    user_module = import_user_module(sa_example_text)
    models = SQLAlchemyModelCombine.retrieve_models_from_module(user_module)
    assert isinstance(models, list)
    assert len(models) == 2


def test_retrieve_djangoorm_models_from_module():
    user_module = import_user_module(djangoorm_example_text)
    models = django_combine.retrieve_models_from_module(user_module)
    assert isinstance(models, list)
    assert len(models) == 2


def test_to_core_model():
    result_models = []

    for combine in (SQLAlchemyModelCombine(), DjangoOrmModelCombine()):
        if isinstance(combine, SQLAlchemyModelCombine):
            example_text = sa_example_text
        if isinstance(combine, DjangoOrmModelCombine):
            example_text = djangoorm_example_text
        module = import_user_module(example_text)
        models = combine.retrieve_models_from_module(module)
        user_core_model = combine.to_core_model(models[0])
        payment_core_model = combine.to_core_model(models[1])
        result_models.append(user_core_model)

        # check metadata
        assert user_core_model.tablename == "user"
        assert user_core_model.unique_together == (("level", "coeff"),)

        # check types
        assert user_core_model.nickname.sql_type == str
        assert user_core_model.level.sql_type == int
        assert user_core_model.is_active.sql_type == bool
        assert user_core_model.coeff.sql_type == float
        assert user_core_model.signature.sql_type == bytes
        assert user_core_model.birthday.sql_type == datetime.date
        assert user_core_model.reg_time.sql_type == datetime.datetime
        assert user_core_model.balance.sql_type == decimal.Decimal

        # check defaults
        assert user_core_model.is_active.default is True
        assert 1 < user_core_model.coeff.default < 2

        assert user_core_model.reg_time.spec_params['auto_on_create']
        assert not user_core_model.reg_time.spec_params.get('auto_on_update')

        assert user_core_model.reg_time.spec_params['auto_on_create']
        assert user_core_model.birthday.spec_params['auto_on_update']

        # check decimal params
        assert user_core_model.balance.spec_params["precision"] == 2
        assert user_core_model.balance.spec_params["scale"] == 10

        # check foreign keys
        assert payment_core_model.user_id.foreign_key == "User.id"

        # check unique
        assert user_core_model.nickname.unique


def test_sa_from_core_model():
    sa_user_model = sa_combine.from_core_model(user_core_model)
    sa_payment_model = sa_combine.from_core_model(payment_core_model)

    assert sa_user_model.__tablename__ == "user"
    assert isinstance(sa_user_model.__table_args__[0], sa.UniqueConstraint)
    assert [i.name for i in sa_user_model.__table_args__[0].columns] == [
        "level",
        "coeff",
    ]

    assert sa_user_model.id.primary_key
    assert sa_payment_model.id.primary_key

    assert sa_user_model.nickname.type.length == 32
    assert sa_user_model.nickname.unique
    assert sa_user_model.nickname.type.python_type == str

    assert sa_user_model.level.type.python_type == int

    assert sa_user_model.is_active.default.arg is True
    assert sa_user_model.is_active.type.python_type == bool

    assert 1 < sa_user_model.coeff.default.arg < 2
    assert sa_user_model.coeff.type.python_type == float

    assert sa_user_model.signature.type.python_type == bytes

    assert sa_user_model.reg_time.default.arg.__name__ == 'utcnow'
    assert not sa_user_model.reg_time.onupdate
    assert sa_user_model.reg_time.type.python_type == datetime.datetime

    assert sa_user_model.birthday.default.arg.__name__ == 'utcnow'
    assert sa_user_model.birthday.onupdate.arg.__name__ == 'utcnow'
    assert sa_user_model.birthday.type.python_type == datetime.date

    assert sa_user_model.balance.type.python_type == decimal.Decimal
    assert sa_user_model.balance.type.precision == 2
    assert sa_user_model.balance.type.scale == 10


def test_basic_model_to_djangoorm_model():
    django_model_user = django_combine.from_core_model(user_core_model)
    django_payment_model = django_combine.from_core_model(payment_core_model)

    assert django_model_user._meta.db_table == "user"
    assert django_model_user._meta.unique_together[0] == (("level", "coeff"),)

    assert django_model_user.id.field.primary_key
    assert django_payment_model.id.field.primary_key
    assert isinstance(django_model_user.id.field, dm.IntegerField)
    assert isinstance(django_payment_model.id.field, dm.IntegerField)

    assert django_model_user.nickname.field.max_length == 32
    assert isinstance(django_model_user.nickname.field, dm.CharField)

    assert isinstance(django_model_user.level.field, dm.IntegerField)

    assert django_model_user.is_active.field.default is True
    assert isinstance(django_model_user.is_active.field, dm.BooleanField)

    assert 1 < django_model_user.coeff.field.default < 2
    assert isinstance(django_model_user.coeff.field, dm.FloatField)

    assert isinstance(django_model_user.signature.field, dm.BinaryField)

    assert django_model_user.reg_time.field.auto_now
    assert isinstance(django_model_user.reg_time.field, dm.DateTimeField)

    assert (
        django_model_user.birthday.field.auto_now_add
    )
    assert isinstance(django_model_user.birthday.field, dm.DateField)

    assert isinstance(django_model_user.balance.field, dm.DecimalField)

    assert django_model_user.balance.field.decimal_places == 2
    assert django_model_user.balance.field.max_digits == 10

    assert django_model_user.nickname.field.unique
