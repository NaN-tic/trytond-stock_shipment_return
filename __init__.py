# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import shipment


def register():
    Pool.register(
        shipment.Move,
        shipment.ShipmentInReturn,
        shipment.ReturnShipmentInStart,
        module='stock_shipment_return', type_='model')
    Pool.register(
        shipment.ReturnShipmentIn,
        module='stock_shipment_return', type_='wizard')
