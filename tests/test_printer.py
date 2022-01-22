from conftest import *


def test_printers():
    for setup in (
        SaSetupFixture,
        DjangoSetupFixture,
    ):
        sa_model_user = setup.combine().from_core_model(user_core_model)
        sa_model_payment = setup.combine().from_core_model(payment_core_model)
        user_printer = setup.model_printer(sa_model_user)
        payment_printer = setup.model_printer(sa_model_payment)
        assert user_printer.print_model() and payment_printer.print_model()
        module_printer = setup.module_printer(user_printer, payment_printer)
        module_repr = module_printer.print_module()
        assert module_repr
