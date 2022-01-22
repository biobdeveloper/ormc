from core.printers import ModelPrinter, ModulePrinter
from orms_tools.django_tools.dj_combine import DjangoOrmModelCombine


class DjangoModulePrinter(ModulePrinter):
    orm: str = "django"

    def print_import_types(self):
        for m in self.model_printers:
            model_imports = m.get_import_types()
            self.imports.update(model_imports)
        return f"from django.db.models import {', '.join(self.imports)}"

    def print_import_base_data(self):
        return "from django.db.models import Model, DO_NOTHING"


class DjangoModelPrinter(ModelPrinter):
    """"""

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.fields = DjangoOrmModelCombine().get_fields(self.model)

    def nested_iterable_repr(self, iterable):
        if not isinstance(iterable, str):
            for i in iterable:
                self.nested_iterable_repr(i)
        return ", ".join(iterable)

    def get_import_types(self):
        return [field.__class__.__qualname__ for field in self.fields]

    def print_classname(self):
        return f'class {self.model._meta.label.split(".")[-1]}(Model):{self.line_break()}{self.line_space()}"""{self.model.__doc__}"""'

    def print_metadata(self):
        """"""
        doc_repr = f"{self.line_space()}class Meta:"
        tablename_repr = f'{self.line_space()}{self.line_space()}db_table = "{self.model._meta.db_table}"'
        if self.model._meta.unique_together:
            unique_together_repr = (
                f"{self.line_space()}{self.line_space()}unique_together = ("
            )

            for unique_combo in self.model._meta.unique_together:
                unique_fields_repr = ", ".join(
                    [f"{unique_filed}" for unique_filed in unique_combo]
                )
                unique_together_repr += unique_fields_repr + ", "
            unique_together_repr += ")"
        else:
            unique_together_repr = ""
        return self.line_break().join([doc_repr, tablename_repr, unique_together_repr])

    def print_field(self, field):
        type_repr = field.__class__.__qualname__
        field_repr = f"{field.name} = {type_repr}"

        if type_repr == "ForeignKey":
            foreign_key_repr = f"{field.related_model.split('.')[0].capitalize()}, on_delete=DO_NOTHING"
        else:
            foreign_key_repr = ""
        type_args = []
        for type_arg in ("max_length", "max_digits", "decimal_places"):
            if hasattr(field, type_arg) and getattr(field, type_arg) is not None:
                type_args.append(f"{type_arg}={getattr(field, type_arg)}")

        primary_key_repr = "primary_key=True" if field.primary_key else ""
        default_repr = (
            f"default={field.default}"
            if field.default
            and not field.primary_key
            and not type_repr in ("DateField", "DateTimeField")
            else ""
        )
        nullable_repr = (
            f"null=False" if field.null is False and not field.primary_key else ""
        )
        unique_repr = "unique=True" if field.unique and not field.primary_key else ""
        doc_repr = f"help_text='{field.verbose_name}'" if field.verbose_name else ""

        if type_repr in ("DateField", "DateTimeField"):
            type_args.append("auto_now=True" if field.auto_now else "")
            type_args.append("auto_now_add=True" if field.auto_now_add else "")

        field_kwargs_repr = ", ".join(
            [
                arg
                for arg in (
                    foreign_key_repr,
                    primary_key_repr,
                    default_repr,
                    nullable_repr,
                    unique_repr,
                    doc_repr,
                    *type_args,
                )
                if arg
            ]
        )

        field_repr += f"({field_kwargs_repr})"
        return field_repr
