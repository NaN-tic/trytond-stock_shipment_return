# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import shipment
from . import purchase


def register():
    Pool.register(
        shipment.Move,
        shipment.ReturnShipmentInStart,
        module='stock_shipment_return', type_='model')
    Pool.register(
        shipment.ShipmentInReturn,
        purchase.Purchase,
        module='stock_shipment_return', type_='model',
        depends=['purchase'])
    Pool.register(
        shipment.ReturnShipmentOutStart,
        module='stock_shipment_return', type_='model',
        dependes=['sale'])
    Pool.register(
        shipment.ReturnShipmentIn,
        module='stock_shipment_return', type_='wizard')
    Pool.register(
        shipment.ReturnShipmentOut,
        depends=['sale'],
        module='stock_shipment_return', type_='wizard')
