# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta

__all__ = ['Purchase']


class Purchase(metaclass=PoolMeta):
    __name__ = 'purchase.purchase'

    def _get_return_shipment(self):
        in_return = super(Purchase, self)._get_return_shipment()
        in_return.origin = self
        return in_return
