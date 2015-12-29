# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelView
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.wizard import Wizard, StateAction, StateView, Button

__all__ = ['Move', 'ReturnShipmentInStart', 'ReturnShipmentIn']
__metaclass__ = PoolMeta


class Move:
    __name__ = 'stock.move'

    @classmethod
    def _get_origin(cls):
        origins = super(Move, cls)._get_origin()
        return origins + ['stock.move']


class ReturnShipmentInStart(ModelView):
    'Return Supplier Shipment'
    __name__ = 'stock.shipment.in.return_shipment.start'


class ReturnShipmentIn(Wizard):
    'Return Supplier Shipment'
    __name__ = 'stock.shipment.in.return_shipment'
    start = StateView('stock.shipment.in.return_shipment.start',
        'stock_shipment_return.return_shipment_in_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Return', 'return_', 'tryton-ok', default=True),
            ])
    return_ = StateAction('stock.act_shipment_in_return_form')

    def do_return_(self, action):
        pool = Pool()
        Move = pool.get('stock.move')
        ShipmentIn = pool.get('stock.shipment.in')
        ShipmentInReturn = pool.get('stock.shipment.in.return')

        shipment_in_ids = Transaction().context['active_ids']
        shipment_in_returns = []
        for shipment_in in ShipmentIn.browse(shipment_in_ids):
            shipment_in_return = ShipmentInReturn()
            shipment_in_return.company = shipment_in.company
            shipment_in_return.reference = shipment_in.code
            shipment_in_return.from_location = shipment_in.warehouse_storage
            shipment_in_return.to_location = shipment_in.supplier_location
            shipment_in_return.save()
            for inv_move in shipment_in.inventory_moves:
                Move.copy([inv_move], {
                        'shipment': str(shipment_in_return),
                        'from_location': inv_move.to_location.id,
                        'to_location': shipment_in.supplier_location.id,
                        'effective_date': None,
                        'planned_date': None,
                        # 'unit_price': inv_move.origin.unit_price,
                        # 'currency': inv_move.origin.currency.id,
                        'unit_price': inv_move.product.cost_price,
                        'currency': inv_move.company.currency.id,
                        'origin': str(inv_move),
                    })
            shipment_in_returns.append(shipment_in_return)

        data = {'res_id': [s.id for s in shipment_in_returns]}
        if len(shipment_in_returns) == 1:
            action['views'].reverse()
        return action, data
