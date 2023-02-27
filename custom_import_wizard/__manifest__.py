# pylint: disable=missing-docstring
# Copyright 2020 VentorTech OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "Custom Import Wizard",
    "category": "Tools",
    "version": "16.0.1.0.0",
    "website": "https://ventor.tech",
    "author": "VentorTech OU",
    "license": "LGPL-3",
    "depends": [],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/custom_import_history.xml",
        "wizard/custom_import_wizard.xml",
        "wizard/info_result_import_wizard.xml",
    ],
    "external_dependencies": {"python": ["xlrd"]},
    "installable": True,
}
