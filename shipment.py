# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelView, fields
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.wizard import Wizard, StateAction, StateView, Button

__all__ = ['Move', 'ShipmentInReturn',
    'ReturnShipmentInStart', 'ReturnShipmentIn',
    'ReturnShipmentOutStart', 'ReturnShipmentOut']


class Move(metaclass=PoolMeta):
    __name__ = 'stock.move'

    @classmethod
    def _get_origin(cls):
        models = super(Move, cls)._get_origin()
        if 'stock.move' not in models:
            models.append('stock.move')
        return models


class ShipmentInReturn(metaclass=PoolMeta):
    __name__ = 'stock.shipment.in.return'
    origin = fields.Reference('Origin', selection=[
                (None, ''),
                ('stock.shipment.in', 'Shipment In'),
                ('purchase.purchase', 'Purchase'),
            ], select=True, readonly=True)


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

        shipment_in_ids = Transaction().context['active_ids']
        shipment_in_returns = []
        for shipment_in in ShipmentIn.browse(shipment_in_ids):
            shipment_in_return = self._get_return_shipment(shipment_in)
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
                        'origin': None,
                        })
            shipment_in_returns.append(shipment_in_return)

        data = {'res_id': [s.id for s in shipment_in_returns]}
        if len(shipment_in_returns) == 1:
            action['views'].reverse()
        return action, data

    def _get_return_shipment(self, shipment_in):
        pool = Pool()
        ShipmentInReturn = pool.get('stock.shipment.in.return')
        shipment = ShipmentInReturn()
        shipment.company = shipment_in.company
        shipment.reference = shipment_in.number
        shipment.from_location = shipment_in.warehouse_storage
        shipment.to_location = shipment_in.supplier_location
        shipment.origin = shipment_in
        shipment.supplier = shipment_in.supplier
        return shipment


class ReturnShipmentOutStart(ModelView):
    'Return Customer Shipment'
    __name__ = 'stock.shipment.out.return_shipment.start'


class ReturnShipmentOut(Wizard):
    'Return Customer Shipment'
    __name__ = 'stock.shipment.out.return_shipment'
    start = StateView('stock.shipment.out.return_shipment.start',
        'stock_shipment_return.return_shipment_out_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Return', 'return_', 'tryton-ok', default=True),
            ])
    return_ = StateAction('stock.act_shipment_out_return_form')

    def do_return_(self, action):
        pool = Pool()
        Move = pool.get('stock.move')
        ShipmentOut = pool.get('stock.shipment.out')

        shipment_out_ids = Transaction().context['active_ids']
        shipment_out_returns = []
        for shipment_out in ShipmentOut.browse(shipment_out_ids):
            shipment_out_return = self._get_return_shipment(shipment_out)
            shipment_out_return.save()
            for inv_move in shipment_out.inventory_moves:
                Move.copy([inv_move], {
                        'shipment': str(shipment_out_return),
                        'from_location': (
                            shipment_out.customer.customer_location),
                        'to_location': shipment_out.warehouse.input_location,
                        'effective_date': None,
                        'planned_date': None,
                        'unit_price': inv_move.product.cost_price,
                        'currency': inv_move.company.currency.id,
                        'origin': ('stock.move,%s' % inv_move.id),
                        })
            shipment_out_returns.append(shipment_out_return)

        data = {'res_id': [s.id for s in shipment_out_returns]}
        if len(shipment_out_returns) == 1:
            action['views'].reverse()
        return action, data

    def _get_return_shipment(self, shipment_out):
        pool = Pool()
        ShipmentOutReturn = pool.get('stock.shipment.out.return')
        shipment = ShipmentOutReturn()
        shipment.customer = shipment_out.customer
        shipment.delivery_address = shipment_out.delivery_address
        shipment.company = shipment_out.company
        shipment.reference = shipment_out.number
        # TIP: known shipment origin with stock_origin module
        if hasattr(ShipmentOutReturn, 'origin_shipment'):
            shipment.origin_shipment = shipment_out
        return shipment
