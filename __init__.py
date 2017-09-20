# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import shipment
from . import purchase


def register():
    Pool.register(
        shipment.Move,
        shipment.ShipmentInReturn,
        shipment.ShipmentOutReturn,
        shipment.ReturnShipmentInStart,
        shipment.ReturnShipmentOutStart,
        purchase.Purchase,
        module='stock_shipment_return', type_='model')
    Pool.register(
        shipment.ReturnShipmentIn,
        shipment.ReturnShipmentOut,
        module='stock_shipment_return', type_='wizard')
