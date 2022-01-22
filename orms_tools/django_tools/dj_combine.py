import os
from datetime import date as date_type
from datetime import datetime as datetime_type
from decimal import Decimal

from django.db import models as dm

from core.combine import AbstractModelCombine
from core.db_primitives import CoreField, CoreModel


APP_LABEL = "djfake"


class DjangoOrmModelCombine(AbstractModelCombine):
    metaclass = dm.base.ModelBase

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        os.environ.setdefault(
            "DJANGO_SETTINGS_MODULE",
            f"orms_tools.django_tools.{APP_LABEL}.{APP_LABEL}.settings",
        )
        import django

        django.setup()

    @classmethod
    def is_model(cls, model):
        return issubclass(model.__class__, cls.metaclass)

    @classmethod
    def integer(cls, **kwargs):
        return dm.IntegerField

    @classmethod
    def character(cls, **kwargs):
        return dm.CharField

    @classmethod
    def boolean(cls, **kwargs):
        return dm.BooleanField

    @classmethod
    def float(cls, **kwargs):
        return dm.FloatField

    @classmethod
    def bytes(cls, **kwargs):
        field = dm.BinaryField
        setattr(field, "__qualname__", "BinaryField")
        return field

    @classmethod
    def decimal(cls, **kwargs):
        return dm.DecimalField

    @classmethod
    def date(cls, **kwargs):
        return dm.DateField

    @classmethod
    def datetime(cls, **kwargs):
        if kwargs.get("auto_now") or kwargs.get("auto_now_add"):
            pass
        return dm.DateTimeField

    def get_fields(self, model: dm.Model):
        """Get fields from Django model"""
        if hasattr(model, "_meta"):
            return [f for f in model._meta.fields]
        else:
            return [f for f in model.fields]

    def to_core_model(self, model: dm.Model):
        """Convert ORM model to CoreModel"""
        return CoreModel(
            tablename=model._meta.db_table,
            unique_together=model._meta.unique_together,
            doc=model.__doc__,
            fields=[self.to_core_field(field) for field in self.get_fields(model)],
        )

    def to_core_field(self, field: dm.Field):
        """Convert ORM field to CoreField"""
        spec_params = {}
        sql_type = None
        name = field.column

        field_kwargs = dict(
            name=name,
            nullable=field.null,
            primary_key=field.primary_key,
            doc=field.verbose_name,
            unique=field.unique,
            default=field.default if field.default != dm.NOT_PROVIDED else None,
        )

        if isinstance(field, dm.ForeignKey):
            original_type = type(field.foreign_related_fields[0])
            foreign_key = f"{field.foreign_related_fields[0].model.__qualname__}.{field.foreign_related_fields[0].attname}"
            field_kwargs["foreign_key"] = foreign_key
        else:
            original_type = type(field)

        original_type_name = original_type.__qualname__
        for core_type, django_type in self.type_map.items():
            suggested_type = django_type()
            suggested_type = suggested_type.__qualname__
            compare = original_type_name == suggested_type
            if compare:
                sql_type = core_type
                break
        if not sql_type:
            raise NotImplementedError(
                f"Django {type(field)} is not currently implemented"
            )
        if original_type_name == "DecimalField":
            if field.decimal_places:
                spec_params["precision"] = field.decimal_places
            if field.max_digits:
                spec_params["scale"] = field.max_digits
        if original_type_name in ("DateField", "DateTimeField"):
            if field.auto_now:
                spec_params["auto_on_create"] = True
            if field.auto_now_add:
                spec_params["auto_on_create"] = True
                spec_params["auto_on_update"] = True
        field_kwargs["sql_type"] = sql_type

        return CoreField(**field_kwargs, **spec_params)

    def from_core_model(self, model: CoreModel) -> dm.Model:
        """Convert CoreModel to SQLAlchemy"""
        django_fields = [self.from_core_field(field) for field in model.fields]
        fields_as_dict = {f.name: f for f in django_fields}
        meta_kwargs = {"db_table": model.tablename, "app_label": APP_LABEL}
        if model.unique_together:
            meta_kwargs["unique_together"] = [model.unique_together]
        meta = type("Meta", (object,), meta_kwargs)

        django_model = dm.base.ModelBase(
            model.tablename.capitalize(),
            (dm.Model,),
            {"Meta": meta, "__module__": "test", **fields_as_dict},
        )
        return django_model

    def from_core_field(self, field: CoreField) -> dm.Field:
        """Convert SQLAlchemy field to CoreField"""

        column_kwargs = dict(
            name=field.name,
            primary_key=field.primary_key,
            verbose_name=field.doc,
            default=field.default,
            null=field.nullable,
            unique=field.unique,
            db_column=field.name,
            help_text=field.doc,
        )

        if field.foreign_key:
            django_type = dm.ForeignKey
            column_kwargs["to"] = field.foreign_key.lower()
            column_kwargs["on_delete"] = dm.DO_NOTHING  # TODO
        else:
            django_type = self.type_map[field.sql_type](**column_kwargs)
        django_field_spec_params = {}

        if field.spec_params:
            if field.sql_type == Decimal:
                if field.spec_params.get("scale"):
                    django_field_spec_params["max_digits"] = field.spec_params["scale"]
                if field.spec_params.get("precision"):
                    django_field_spec_params["decimal_places"] = field.spec_params[
                        "precision"
                    ]
            if field.sql_type in (date_type, datetime_type):
                if field.spec_params.get("auto_on_update"):
                    django_field_spec_params["auto_now_add"] = True
                elif field.spec_params.get("auto_on_create"):
                    django_field_spec_params["auto_now"] = True
            if field.spec_params.get("length"):
                django_field_spec_params["max_length"] = field.spec_params["length"]
            column_kwargs.update(**django_field_spec_params)
        django_field = django_type(**column_kwargs)
        return django_field
