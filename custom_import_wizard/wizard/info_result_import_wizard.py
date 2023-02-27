# Copyright 2020 VentorTech OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

# Odoo:
from odoo import fields, models


class InfoResultImportWizard(models.TransientModel):
    _name = "info.result.import.wizard"
    _description = "Info Result Import Wizard"
    message = fields.Char(string="Info: ", readonly=True, store=True)
