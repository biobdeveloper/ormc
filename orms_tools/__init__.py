from orms_tools.django_tools.dj_combine import DjangoOrmModelCombine
from orms_tools.django_tools.dj_printers import DjangoModelPrinter, DjangoModulePrinter
from orms_tools.sqlalchemy_tools.sa_combine import SQLAlchemyModelCombine
from orms_tools.sqlalchemy_tools.sa_printers import (
    SqlAlchemyModelPrinter,
    SqlAlchemyModulePrinter,
)

model_printers = {
    "sa": SqlAlchemyModelPrinter,
    "django": DjangoModelPrinter,
}

module_printers = {
    "sa": SqlAlchemyModulePrinter,
    "django": DjangoModulePrinter,
}

combines = {
    "sa": SQLAlchemyModelCombine,
    "django": DjangoOrmModelCombine,
}
