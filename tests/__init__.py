# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
try:
    from trytond.modules.stock_shipment_return.tests.test_stock_shipment_return import suite
except ImportError:
    from .test_stock_shipment_return import suite

__all__ = ['suite']
