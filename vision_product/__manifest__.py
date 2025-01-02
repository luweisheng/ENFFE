# -*- coding: utf-8 -*-
{
    'name': "工程技术",

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
    'depends': ['base', 'mail', 'web'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/product_group.xml',
        'views/res_company.xml',
        'views/vision_product_menu.xml',
        'views/packing_type.xml',
        'views/product.xml',
        'views/product_category.xml',
        'views/bom.xml',
        'views/uom.xml',
        'views/product_attribute.xml',
        'views/res_supplier.xml',
        'views/product_price.xml',
        'views/bulk_maintenance_price_list.xml',
        'views/design_standard.xml',
    ],

    # 'assets': {
    #     'web.assets_backend': [
    #         'bysco_engineering_technology/static/css/vision.scss',
    #     ],
    # },
    # only loaded in demonstration mode

    'demo': [
        'demo/demo.xml',
    ],
    'images': [
        'static/description/icon.png',
    ],
}

