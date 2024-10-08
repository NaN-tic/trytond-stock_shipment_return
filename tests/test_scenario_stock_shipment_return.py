import datetime
import unittest
from decimal import Decimal

from proteus import Model, Wizard
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.tests.test_tryton import drop_db
from trytond.tests.tools import activate_modules


class Test(unittest.TestCase):

    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):

        # Install stock_shipment_return Module
        config = activate_modules(
            ['stock_shipment_return', 'sale', 'stock_origin'])

        # Create company
        _ = create_company()
        company = get_company()

        # Create supplier
        Party = Model.get('party.party')
        supplier = Party(name='Supplier')
        supplier.save()

        # Create customer
        customer = Party(name='Customer')
        customer.save()

        # Create product
        ProductUom = Model.get('product.uom')
        ProductTemplate = Model.get('product.template')
        Product = Model.get('product.product')
        unit, = ProductUom.find([('name', '=', 'Unit')])
        template = ProductTemplate()
        template.name = 'Product 1'
        template.default_uom = unit
        template.type = 'goods'
        template.list_price = Decimal('20')
        template.cost_price = Decimal('8')
        template.save()
        product, = template.products
        template = ProductTemplate()
        template.name = 'Product 2'
        template.default_uom = unit
        template.type = 'goods'
        template.list_price = Decimal('30')
        template.cost_price = Decimal('15')
        template.save()
        product2, = template.products

        # Get stock locations
        Location = Model.get('stock.location')
        warehouse_loc, = Location.find([('code', '=', 'WH')])
        supplier_loc, = Location.find([('code', '=', 'SUP')])
        customer_loc, = Location.find([('code', '=', 'CUS')])
        output_loc, = Location.find([('code', '=', 'OUT')])
        storage_loc, = Location.find([('code', '=', 'STO')])

        # Receive products
        today = datetime.date.today()
        ShipmentIn = Model.get('stock.shipment.in')
        shipment_in = ShipmentIn()
        shipment_in.planned_date = today
        shipment_in.supplier = supplier
        shipment_in.company = company
        incoming_move = shipment_in.incoming_moves.new()
        incoming_move.product = product
        incoming_move.quantity = 100
        incoming_move.from_location = supplier_loc
        incoming_move.to_location = shipment_in.warehouse_input
        incoming_move.unit_price = Decimal(0)
        incoming_move.currency = company.currency
        incoming_move = shipment_in.incoming_moves.new()
        incoming_move.product = product2
        incoming_move.quantity = 200
        incoming_move.from_location = supplier_loc
        incoming_move.to_location = shipment_in.warehouse_input
        incoming_move.unit_price = Decimal(0)
        incoming_move.currency = company.currency
        shipment_in.save()
        shipment_in.click('receive')
        shipment_in.click('do')

        # Check available quantities
        config._context.update({
            'locations': [storage_loc.id],
            'stock_date_end': today
        })
        product = Product(product.id, config._context)
        self.assertEqual(product.quantity, 100.0)
        product2 = Product(product2.id, config._context)
        self.assertEqual(product2.quantity, 200.0)

        # Return some products using the wizard
        ShipmentInReturn = Model.get('stock.shipment.in.return')
        return_shipment = Wizard('stock.shipment.in.return_shipment',
                                 [shipment_in])
        return_shipment.execute('return_')
        returned_shipment, = ShipmentInReturn.find([
            ('state', '=', 'draft'),
        ])
        product2move = {m.product.id: m for m in returned_shipment.moves}
        self.assertEqual(product2move[product.id].quantity, 100.0)
        self.assertEqual(product2move[product2.id].quantity, 200.0)
        product2move[product.id].quantity = 50
        returned_shipment.moves.remove(product2move[product2.id])
        returned_shipment.save()
        self.assertEqual(sorted([x.quantity for x in returned_shipment.moves]),
                         [50.0])

        # Process returning shipment
        returned_shipment.click('wait')
        returned_shipment.click('assign_try')
        returned_shipment.click('do')

        # Check available quantities
        config._context.update({
            'locations': [storage_loc.id],
            'stock_date_end': today
        })
        product = Product(product.id, config._context)
        self.assertEqual(product.quantity, 50.0)
        product2 = Product(product2.id, config._context)
        self.assertEqual(product2.quantity, 200.0)

        # Create Shipment Out
        ShipmentOut = Model.get('stock.shipment.out')
        shipment_out = ShipmentOut()
        shipment_out.planned_date = today
        shipment_out.customer = customer
        shipment_out.warehouse = warehouse_loc
        shipment_out.company = company
        outgoing_move = shipment_out.outgoing_moves.new()
        outgoing_move.product = product
        outgoing_move.unit = unit
        outgoing_move.quantity = 1
        outgoing_move.from_location = output_loc
        outgoing_move.to_location = customer_loc
        outgoing_move.company = company
        outgoing_move.unit_price = Decimal('1')
        outgoing_move.currency = company.currency
        shipment_out.save()
        shipment_out.click('wait')

        # Return some products using the wizard
        ShipmentOutReturn = Model.get('stock.shipment.out.return')
        return_shipment = Wizard('stock.shipment.out.return_shipment',
                                 [shipment_out])
        return_shipment.execute('return_')
        returned_shipment, = ShipmentOutReturn.find([
            ('state', '=', 'draft'),
        ])
        returned_shipment.click('receive')
        self.assertEqual(len(returned_shipment.inventory_moves), 1)
        self.assertEqual(len(returned_shipment.incoming_moves), 1)
