"""
    Copyright 2020 VentorTech OU
    License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).
"""

# Stdlib:
from datetime import datetime

# Odoo:
from odoo import fields, models


# pylint: disable=too-few-public-methods
class CustomImportHistory(models.Model):
    """ History for import """

    _name = "custom.import.history"
    _description = "Custom Import History"

    name = fields.Datetime(default=lambda self: datetime.now(), string="Import Date")
    original_file = fields.Binary()
    formatted_file = fields.Binary()
    original_file_name = fields.Char()
    formatted_file_name = fields.Char()
    total_imported = fields.Integer()
    total_duplicated = fields.Integer()
    total_errors = fields.Integer()
    user_id = fields.Many2one("res.users", default=lambda self: self.env.user)
    model = fields.Char()
    extra_info = fields.Char()
    error_details = fields.Char()
