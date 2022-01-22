from abc import ABC, abstractmethod
from datetime import date as date_type
from datetime import datetime as datetime_type
from decimal import Decimal
from typing import Dict, List


class AbstractModelCombine(ABC):
    """Abstract Model Combine."""
    fields: list = []
    foreign_keys: list
    primary_keys: list
    constraints: list

    type_map: Dict

    def __init__(self):

        self.type_map = {
            int: self.integer,
            str: self.character,
            bool: self.boolean,
            float: self.float,
            Decimal: self.decimal,
            date_type: self.date,
            datetime_type: self.datetime,
            bytes: self.bytes,
        }

    @classmethod
    @abstractmethod
    def is_model(cls, model):
        """Check object is an ORM Model object"""

    @classmethod
    @abstractmethod
    def integer(cls, **kwargs):
        """Integer"""

    @classmethod
    @abstractmethod
    def character(cls, **kwargs):
        """Varchar"""

    @classmethod
    @abstractmethod
    def boolean(cls, **kwargs):
        """Boolean"""

    @classmethod
    @abstractmethod
    def float(cls, **kwargs):
        """Float"""

    @classmethod
    @abstractmethod
    def bytes(cls, **kwargs):
        """Binary"""

    @classmethod
    @abstractmethod
    def decimal(cls, **kwargs):
        """Decimal"""

    @classmethod
    @abstractmethod
    def date(cls, **kwargs):
        """Date"""

    @classmethod
    @abstractmethod
    def datetime(cls, **kwargs):
        """DateTime"""

    @staticmethod
    @abstractmethod
    def get_fields(self, model):
        """Get fields from model"""

    @staticmethod
    @abstractmethod
    def from_core_model(model):
        """Convert CoreModel to ORM Model"""

    @staticmethod
    @abstractmethod
    def to_core_model(model):
        """Convert ORM model to CoreModel"""

    @staticmethod
    @abstractmethod
    def from_core_field(model):
        """Convert CoreField to ORM field"""

    @staticmethod
    @abstractmethod
    def to_core_field(model):
        """Convert ORM field to CoreField"""

    @classmethod
    def retrieve_models_from_module(cls, module) -> List:
        """Retrieve models from module"""
        return [model for model in module.__dict__.values() if cls.is_model(model)]
