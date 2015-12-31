=================================
Stock Shipment In Return Scenario
=================================

=============
General Setup
=============

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from proteus import config, Model, Wizard
    >>> today = datetime.date.today()
    >>> yesterday = today - relativedelta(days=1)

Create database::

    >>> config = config.set_trytond()
    >>> config.pool.test = True

Install stock_shipment_return Module::

    >>> Module = Model.get('ir.module.module')
    >>> modules = Module.find([('name', '=', 'stock_shipment_return')])
    >>> Module.install([x.id for x in modules], config.context)
    >>> Wizard('ir.module.module.install_upgrade').execute('upgrade')

Create company::

    >>> Currency = Model.get('currency.currency')
    >>> CurrencyRate = Model.get('currency.currency.rate')
    >>> Company = Model.get('company.company')
    >>> Party = Model.get('party.party')
    >>> company_config = Wizard('company.company.config')
    >>> company_config.execute('company')
    >>> company = company_config.form
    >>> party = Party(name='Dunder Mifflin')
    >>> party.save()
    >>> company.party = party
    >>> currencies = Currency.find([('code', '=', 'USD')])
    >>> if not currencies:
    ...     currency = Currency(name='U.S. Dollar', symbol='$', code='USD',
    ...         rounding=Decimal('0.01'), mon_grouping='[3, 3, 0]',
    ...         mon_decimal_point='.', mon_thousands_sep=',')
    ...     currency.save()
    ...     CurrencyRate(date=today + relativedelta(month=1, day=1),
    ...         rate=Decimal('1.0'), currency=currency).save()
    ... else:
    ...     currency, = currencies
    >>> company.currency = currency
    >>> company_config.execute('add')
    >>> company, = Company.find()

Reload the context::

    >>> User = Model.get('res.user')
    >>> config._context = User.get_preferences(True, config.context)

Create supplier::

    >>> Party = Model.get('party.party')
    >>> supplier = Party(name='Supplier')
    >>> supplier.save()

Create category::

    >>> ProductCategory = Model.get('product.category')
    >>> category = ProductCategory(name='Category')
    >>> category.save()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> template = ProductTemplate()
    >>> template.name = 'Product 1'
    >>> template.category = category
    >>> template.default_uom = unit
    >>> template.type = 'goods'
    >>> template.list_price = Decimal('20')
    >>> template.cost_price = Decimal('8')
    >>> template.save()
    >>> product, = template.products

    >>> template = ProductTemplate()
    >>> template.name = 'Product 2'
    >>> template.category = category
    >>> template.default_uom = unit
    >>> template.type = 'goods'
    >>> template.list_price = Decimal('30')
    >>> template.cost_price = Decimal('15')
    >>> template.save()
    >>> product2, = template.products

Get stock locations::

    >>> Location = Model.get('stock.location')
    >>> warehouse_loc, = Location.find([('code', '=', 'WH')])
    >>> supplier_loc, = Location.find([('code', '=', 'SUP')])
    >>> input_loc, = Location.find([('code', '=', 'IN')])
    >>> storage_loc, = Location.find([('code', '=', 'STO')])

Receive products::

    >>> ShipmentIn = Model.get('stock.shipment.in')
    >>> shipment_in = ShipmentIn()
    >>> shipment_in.planned_date = today
    >>> shipment_in.supplier = supplier
    >>> shipment_in.company = company
    >>> incoming_move = shipment_in.incoming_moves.new()
    >>> incoming_move.product = product
    >>> incoming_move.quantity = 100
    >>> incoming_move.from_location = supplier_loc
    >>> incoming_move.to_location = shipment_in.warehouse_input
    >>> incoming_move = shipment_in.incoming_moves.new()
    >>> incoming_move.product = product2
    >>> incoming_move.quantity = 200
    >>> incoming_move.from_location = supplier_loc
    >>> incoming_move.to_location = shipment_in.warehouse_input
    >>> shipment_in.save()
    >>> shipment_in.click('receive')
    >>> shipment_in.click('done')

Check available quantities::

    >>> with config.set_context({'locations': [storage_loc.id], 'stock_date_end': today}):
    ...     product.reload()
    ...     product.quantity
    ...     product2.reload()
    ...     product2.quantity
    100.0
    200.0

Return some products using the wizard::

    >>> ShipmentInReturn = Model.get('stock.shipment.in.return')
    >>> return_shipment = Wizard('stock.shipment.in.return_shipment',
    ...     [shipment_in])
    >>> return_shipment.execute('return_')
    >>> returned_shipment, = ShipmentInReturn.find([
    ...     ('state', '=', 'draft'),
    ...     ])
    >>> product2move = {m.product.id: m for m in returned_shipment.moves}
    >>> product2move[product.id].quantity
    100.0
    >>> product2move[product2.id].quantity
    200.0
    >>> product2move[product.id].quantity = 50
    >>> returned_shipment.moves.remove(product2move[product2.id])
    >>> returned_shipment.save()
    >>> sorted([x.quantity for x in returned_shipment.moves])
    [50.0]

Process returning shipment::

    >>> returned_shipment.click('wait')
    >>> returned_shipment.click('assign_try')
    True
    >>> returned_shipment.click('done')

Check available quantities::

    >>> with config.set_context({'locations': [storage_loc.id], 'stock_date_end': today}):
    ...     product.reload()
    ...     product.quantity
    ...     product2.reload()
    ...     product2.quantity
    50.0
    200.0
