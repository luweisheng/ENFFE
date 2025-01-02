# -*- coding: utf-8 -*-
{
    'name': "仓库",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['vision_mrp'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/picking_data.xml',
        'views/stock_menu.xml',
        'views/stock_location.xml',
        'views/stock_picking_type.xml',
        'views/stock_picking.xml',
        'views/promise_group.xml',
        'views/purchase.xml',
        'views/stock_quantity.xml',
        'views/product.xml',
        'views/availability_query.xml',
        'wizard/purchase_stock.xml',
        # 'wizard/purchase_stock_return.xml',
        'wizard/production_stock.xml',
        'wizard/outsource_stock.xml',
        'wizard/done_production_stock.xml',
        'wizard/done_subcontract_production_stock.xml',
        'wizard/sale_stock.xml',
        'wizard/other_stock.xml',
    ],

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

