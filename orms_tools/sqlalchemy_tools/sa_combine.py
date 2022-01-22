import datetime
from typing import List

from sqlalchemy.orm import ColumnProperty, DeclarativeMeta, class_mapper

from core.combine import AbstractModelCombine
from core.db_primitives import CoreField, CoreModel

from .sa_base import SABase, metadata, sa


class SQLAlchemyModelCombine(AbstractModelCombine):
    metaclass = DeclarativeMeta

    def __init__(self, *args):
        super().__init__(*args)

    @classmethod
    def is_model(cls, model):
        return issubclass(model.__class__, cls.metaclass) and hasattr(
            model, "__tablename__"
        )

    @classmethod
    def integer(cls, **kwargs):
        return sa.Integer

    @classmethod
    def character(cls, **kwargs):
        if kwargs.get("length"):
            return sa.String(**kwargs)
        else:
            return sa.Text

    @classmethod
    def boolean(cls, **kwargs):
        return sa.Boolean

    @classmethod
    def float(cls, **kwargs):
        return sa.Float

    @classmethod
    def bytes(cls, **kwargs):
        return sa.BINARY(**kwargs)

    @classmethod
    def decimal(cls, **kwargs):
        return sa.DECIMAL(**kwargs)

    @classmethod
    def date(cls, **kwargs):
        for key in ('auto_on_create', 'auto_on_update'):
            try:
                kwargs.pop(key)
            except KeyError:
                pass
        return sa.Date(**kwargs)

    @classmethod
    def datetime(cls, **kwargs):
        for key in ('auto_on_create', 'auto_on_update'):
            try:
                kwargs.pop(key)
            except KeyError:
                pass
        return sa.DateTime(**kwargs)

    def get_fields(self, model) -> List[ColumnProperty]:
        fields = []
        mapper = class_mapper(model)
        for v in mapper.iterate_properties:
            if isinstance(v, ColumnProperty):
                fields.append(v)
        return fields

    def to_core_model(self, model: SABase) -> CoreModel:
        """Convert SQLAlchemy Model to CoreModel"""
        model_kwargs = {
            "tablename": model.__tablename__,
            "doc": model.__doc__,
            "fields": [self.to_core_field(field) for field in self.get_fields(model)],
        }
        unique_together = []
        if hasattr(model, "__table_args__"):
            for arg in model.__table_args__:
                if isinstance(arg, sa.UniqueConstraint) and len(arg.columns) > 1:
                    unique_together.append(tuple([col.name for col in arg.columns]))
        if unique_together:
            model_kwargs["unique_together"] = tuple(unique_together)
        return CoreModel(**model_kwargs)

    def to_core_field(self, field: ColumnProperty) -> CoreField:
        """Convert CoreField to SQLAlchemy field"""
        spec_params = {}
        if len(field.columns) != 1:
            raise
        column = field.expression

        sql_type = None
        for core_type in self.type_map.keys():
            if core_type == column.type.python_type:
                sql_type = core_type
                break
        if not sql_type:
            raise

        if column.default:
            default_value = column.default.arg
        else:
            default_value = None

        if isinstance(column.type, (sa.Float, sa.DECIMAL)):
            if column.type.precision:
                spec_params["precision"] = column.type.precision
            if column.type.scale:
                spec_params["scale"] = column.type.scale

        if isinstance(column.type, (sa.Date, sa.DateTime)):
            if hasattr(column.default, 'arg') and column.default.arg.__name__ == 'utcnow':
                spec_params["auto_on_create"] = True
            if hasattr(column.onupdate, 'arg') and column.onupdate.arg.__name__ == 'utcnow':
                spec_params['auto_on_update'] = True

        try:
            foreign_key_column = column.foreign_keys.pop().column
            foreign_key = f"{foreign_key_column.table.name.capitalize()}.{foreign_key_column.name}"
        except KeyError:
            foreign_key = None

        core_field = CoreField(
            name=column.name,
            nullable=column.nullable,
            primary_key=column.primary_key,
            doc=column.doc,
            sql_type=sql_type,
            unique=column.unique,
            default=default_value,
            foreign_key=foreign_key,
            **spec_params,
        )
        return core_field

    def from_core_model(self, model: CoreModel) -> SABase:
        """Convert CoreModel to SQLAlchemy Model"""
        fields = [self.from_core_field(field) for field in model.fields]
        fields_as_dict = {f.name: f for f in fields}
        unique_together = []
        model_kwargs = {
            "__module__": model.__module__,
            "__qualname__": model.tablename.capitalize(),
            "__doc__": model.__doc__,
            "__tablename__": model.tablename,
            **fields_as_dict,
        }
        for unique_seq in model.unique_together:
            unique_together.append(sa.UniqueConstraint(*unique_seq))
        if unique_together:
            model_kwargs["__table_args__"] = tuple(unique_together)
        sa_model = DeclarativeMeta(
            model.tablename.capitalize(),
            (SABase,),
            model_kwargs,
        )
        return sa_model

    def from_core_field(self, field: CoreField) -> sa.Column:
        """Convert SQLAlchemy field to CoreField"""
        sa_type = self.type_map[field.sql_type]
        sa_type_instance = sa_type(**field.spec_params)
        relations = []
        if field.foreign_key:
            relations.append(
                sa.ForeignKey(
                    column=field.foreign_key.lower(),
                    name=field.name,
                ),
            )
        column_kwargs = dict(
            name=field.name,
            primary_key=field.primary_key,
            default=field.default,
            doc=field.doc,
            unique=field.unique,
            nullable=field.nullable,
        )
        if field.spec_params.get('auto_on_create'):
            column_kwargs['default'] = datetime.datetime.utcnow
        if field.spec_params.get('auto_on_update'):
            column_kwargs['onupdate'] = datetime.datetime.utcnow
        sa_field = sa.Column(sa_type_instance, *relations, **column_kwargs)
        return sa_field
