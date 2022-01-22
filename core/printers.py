from abc import ABC, abstractmethod
from typing import List, Tuple


class ModulePrinter(ABC):
    orm: str = "Abstract"
    imports: set
    model_printers: Tuple

    def __init__(self, *model_printers):
        self.imports = set()
        self.model_printers = model_printers

    def collect_import_types(self):
        for m in self.model_printers:
            model_import_types = m.get_import_types()
            self.imports.update(model_import_types)

    @abstractmethod
    def print_import_types(self):
        """"""

    @abstractmethod
    def print_import_base_data(self):
        """"""

    @staticmethod
    def line_break() -> str:
        return """
"""

    def print_module(self):
        """"""
        models_reprs = [m.print_model() for m in self.model_printers]

        import_header_repr = self.line_break().join(
            [self.print_import_types(), self.print_import_base_data()]
        )

        return self.line_break().join([import_header_repr, *models_reprs])


class ModelPrinter(ABC):
    fields: List

    @staticmethod
    def line_break() -> str:
        return """
"""

    @staticmethod
    def line_space():
        return "    "

    @abstractmethod
    def print_classname(self):
        """Print Classname"""

    @abstractmethod
    def print_metadata(self):
        """Print Metadata"""

    @abstractmethod
    def print_field(self, field):
        """Print Field"""

    @abstractmethod
    def get_import_types(self):
        """Retrieve import types"""

    def print_fields(self):
        """Print Fields"""
        return "".join(
            [
                f"{self.line_space()}{self.print_field(f)}{self.line_break()}"
                for f in self.fields
            ]
        )

    def print_model(self) -> str:
        """Print Model."""
        classname = self.print_classname()
        metadata = self.print_metadata()
        fields = self.print_fields()
        return self.line_break().join(
            [
                self.line_break(),
                classname,
                self.line_break(),
                metadata,
                self.line_break(),
                fields,
            ]
        )
