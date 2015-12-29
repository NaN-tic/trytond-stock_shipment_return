# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .shipment import *


def register():
    Pool.register(
        Move,
        ReturnShipmentInStart,
        module='stock_shipment_return', type_='model')
    Pool.register(
        ReturnShipmentIn,
        module='stock_shipment_return', type_='wizard')
