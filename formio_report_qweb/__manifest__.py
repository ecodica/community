# Copyright Nova Code (http://www.novacode.nl)
# See LICENSE file for full licensing details.

{
    'name': 'Forms | QWeb Reports',
    'summary': 'Generate (PDF) reports for every Form',
    'version': '16.0.1.2',
    'author': 'Nova Code',
    'website': 'https://www.novacode.nl',
    'live_test_url': 'https://demo16.novacode.nl',
    'license': 'LGPL-3',
    'category': 'Forms/Forms',
    'depends': [
        'formio',
        'formio_data_api'
    ],
    'application': True,
    'data': [
        'report/formio_form_report_views.xml',
        'report/report_formio_form.xml',
        'report/report_formio_form_components.xml',
        'security/ir_model_access.xml',
        'views/formio_builder_views.xml',
        'views/formio_builder_report_views.xml',
        'views/formio_form_views.xml',
        'wizard/formio_form_report_qweb_wizard.xml'
    ],
    'assets': {
        'web.report_assets_common': [
            'formio_report_qweb/static/src/scss/report_formio_form.scss'
        ],
    },
    'images': [
        'static/description/banner.gif',
    ],
    'description': 'Generate (PDF) reports for every Form',
}
