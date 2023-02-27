﻿# Copyright 2020 VentorTech OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

import json

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    allowed_warehouse_ids = fields.Many2many(
        comodel_name='stock.warehouse',
        string='Allowed Warehouses',
        help='List of all warehouses user has access to',
    )

    custom_package_name = fields.Char(
        string='Custom Build Name',
        compute="_compute_custom_package_name",
        compute_sudo=True,
    )

    ventor_base_version = fields.Char(
        compute="_compute_ventor_base_version",
        compute_sudo=True,
        readonly=True,
    )

    ventor_global_settings = fields.Text(
        string='Global Settings',
        readonly=True,
        compute='_compute_global_settings'
    )

    ventor_user_settings = fields.Text(
        string='User Settings'
    )

    @property
    def SELF_READABLE_FIELDS(self):
        readable_fields = [
            'ventor_global_settings',
            'ventor_user_settings',
            'custom_package_name',
            'ventor_base_version',
        ]
        return super().SELF_READABLE_FIELDS + readable_fields

    @property
    def SELF_WRITEABLE_FIELDS(self):
        writable_fields = ['ventor_user_settings']
        return super().SELF_WRITEABLE_FIELDS + writable_fields

    def _compute_custom_package_name(self):
        custom_package_name = (
            self.env["ir.config_parameter"]
            .get_param("ventor_base.custom_package_name", "")
        )
        self.custom_package_name = custom_package_name

    def _compute_ventor_base_version(self):
        ventor_base_version = (
            self.env["ir.module.module"]
            .search([("name", "=", "ventor_base"), ("state", "=", "installed")])
            .latest_version
        )
        for user in self:
            if ventor_base_version:
                user.ventor_base_version = ventor_base_version
            else:
                user.ventor_base_version = ""

    def _compute_global_settings(self):
        settings = []

        for stock_picking_type in self.env['stock.picking.type'].search([]):
            stock_picking_type_settings = stock_picking_type.get_warehouse_operation_settings()
            if stock_picking_type.code != 'outgoing':
                stock_picking_type_settings['settings'].pop('check_shipping_information')
            if stock_picking_type.code != 'incoming':
                stock_picking_type_settings['settings'].pop('hide_qty_to_receive')
            settings.append(stock_picking_type_settings)

        ventor_option_settings = self.env['ventor.option.setting'].sudo().get_general_settings()
        obj = {'operation_types': settings}
        obj.update(ventor_option_settings)

        self.ventor_global_settings = json.dumps(
            obj=obj,
            indent='    ',
            sort_keys=True
        )

    @api.model
    def create(self, vals):
        result = super().create(vals)
        if not result.allowed_warehouse_ids:
            result.write(
                {
                    'allowed_warehouse_ids': [
                        (
                            6, 0, self.env["stock.warehouse"].sudo().with_context(active_test=False).search([]).ids
                        )
                    ]
                }
            )
        return result

    def write(self, vals):
        result = super().write(vals)
        if result and 'allowed_warehouse_ids' in vals:
            self.env['ir.rule'].clear_cache()
        return result
