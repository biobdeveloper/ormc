import datetime

import sqlalchemy as sa
from sqlalchemy.orm import ColumnProperty

from core.printers import ModelPrinter, ModulePrinter
from orms_tools.sqlalchemy_tools.sa_combine import SQLAlchemyModelCombine


class SqlAlchemyModulePrinter(ModulePrinter):
    orm = "sqlalchemy"

    def print_import_types(self):
        for m in self.model_printers:
            model_imports = m.get_import_types()
            self.imports.update(model_imports)
        return f"from sqlalchemy import {', '.join(self.imports)}"

    def print_import_base_data(self):
        """"""
        return """
import datetime
from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta

metadata = MetaData()
SABase: DeclarativeMeta = declarative_base(metadata=metadata)
"""


class SqlAlchemyModelPrinter(ModelPrinter):
    """"""

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.fields = SQLAlchemyModelCombine().get_fields(self.model)

    def get_import_types(self):
        import_types = [
            field.expression.type.__class__.__qualname__ for field in self.fields
        ]
        import_types.append("Column")
        import_types.append("UniqueConstraint")
        import_types.append("ForeignKey")
        return import_types

    def print_field(self, field: ColumnProperty):
        column = field.expression
        field_repr = f"{field.key} = Column"
        
        type_repr = column.type.__class__.__qualname__
        type_args = []
        for type_arg in ("length", "precision", "scale"):
            if (
                hasattr(column.type, type_arg)
                and getattr(column.type, type_arg) is not None
            ):
                type_args.append(
                    f"{type_arg}={getattr(column.type, type_arg)}"
                )
        type_repr = f'{type_repr}({", ".join(type_args)})'
        try:
            foreign_key_column = column.foreign_keys.pop().column
            foreign_key = (
                foreign_key_column.table.name.capitalize()
                + "."
                + foreign_key_column.name
            )
            foreign_key_repr = f"ForeignKey({foreign_key})"
        except KeyError:
            foreign_key_repr = ""

        if column.primary_key:
            primary_key_repr = "primary_key=True"
        else:
            primary_key_repr = ""

        default_repr = ""
        onupdate_repr = ""

        if hasattr(column.default, 'arg'):
            if column.type.python_type in (datetime.date, datetime.datetime):
                default_repr, onupdate_repr = self._print_datetime_defaults(column)
            else:
                if column.default.is_text:
                    default_value = f"'{column.default.arg}'"
                else:
                    default_value = f"{column.default.arg}"
                if default_value:
                    default_repr = f"default={default_value}"

        nullable = (
            f"nullable=False"
            if (column.nullable is False) and (not column.primary_key)
            else ""
        )
        unique_repr = (
            "unique=True"
            if column.unique and not column.primary_key
            else ""
        )
        doc_repr = f"doc='{column.doc}'" if column.doc else ""

        field_kwargs_repr = ", ".join(
            [
                arg
                for arg in (
                    type_repr,
                    foreign_key_repr,
                    primary_key_repr,
                    default_repr,
                    onupdate_repr,
                    nullable,
                    unique_repr,
                    doc_repr,
                )
                if arg
            ]
        )

        field_repr += f"({field_kwargs_repr})"
        return field_repr

    def print_metadata(self):
        """"""
        tablename_repr = (
            f'{self.line_space()}__tablename__ = "{self.model.__tablename__}"'
        )
        if hasattr(self.model, "__table_args__"):
            args_repr = []
            for arg in self.model.__table_args__:
                if isinstance(arg, sa.UniqueConstraint) and len(arg.columns) > 1:
                    arg_repr = "UniqueConstraint("
                    unique_together_fields_repr = ", ".join(
                        [f"'{i.name}'" for i in arg.columns]
                    )
                    arg_repr += f"{unique_together_fields_repr}),"
                    args_repr.append(arg_repr)

            table_args_repr = (
                f'{self.line_space()}__table_args__ = ({", ".join(args_repr)})'
            )
        else:
            table_args_repr = ""
        return self.line_break().join([tablename_repr, table_args_repr])

    def print_classname(self):
        return f'class {self.model.__tablename__.capitalize()}(SABase):{self.line_break()}{self.line_space()}"""{self.model.__doc__}"""'

    def print_unique_together(self, constraint):
        pass

    def _print_datetime_defaults(self, column):
        default_repr, onupdate_repr = "", ""
        if column.default.arg.__name__ == 'utcnow':
            default_repr = 'default=datetime.datetime.utcnow'
        try:
            if column.onupdate.arg.__name__ == 'utcnow':
                onupdate_repr = 'onupdate=datetime.datetime.utcnow'
        except:
            pass
        return default_repr, onupdate_repr