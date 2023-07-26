# Copyright Nova Code (http://www.novacode.nl)
# See LICENSE file for full licensing details.

{
    'name': 'Forms | Sales',
    'summary': 'Forms integration with Sale Orders/Quotations',
    'version': '16.0.2.0',
    'license': 'LGPL-3',
    'author': 'Nova Code',
    'website': 'https://www.novacode.nl',
    'live_test_url': 'https://demo16.novacode.nl',
    'category': 'Forms/Forms',
    'depends': [
        'sale_management',
        'formio',
        'formio_data_api'
    ],
    'data': [
        'data/formio_sale_data.xml',
        'views/formio_form_views.xml',
        'views/sale_views.xml',
    ],
    'application': True,
    'images': [
        'static/description/banner.gif',
    ],
    'description': 'Forms integration with Sale Orders/Quotations'
}
