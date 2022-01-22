from core.combine import AbstractModelCombine
from core.printers import ModulePrinter
from core.utils import import_user_module, detect_orm
from orms_tools import combines, model_printers, module_printers


class App:
    """Core application class."""

    input_combine: AbstractModelCombine
    output_combine: AbstractModelCombine
    output_module_printer: ModulePrinter

    def __init__(self):
        pass

    def process(self, raw_input_module: str, output_orm: str):
        input_orm = detect_orm(raw_input_module)

        self.input_combine = combines[input_orm]()
        self.output_combine = combines[output_orm]()
        self.output_model_printer = module_printers[output_orm]

        input_module = import_user_module(raw_input_module)
        if not input_module:
            exit("Unable to import module")
        input_models = self.input_combine.retrieve_models_from_module(input_module)

        core_models = [
            self.input_combine.to_core_model(model) for model in input_models
        ]
        output_models = [
            self.output_combine.from_core_model(model) for model in core_models
        ]

        output_models_printers = [
            model_printers[output_orm](model) for model in output_models
        ]
        self.output_module_printer = module_printers[output_orm](
            *output_models_printers
        )

        output_raw_module = self.output_module_printer.print_module()
        return output_raw_module

