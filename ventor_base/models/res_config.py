﻿# Copyright 2020 VentorTech OU
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class VentorConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    logotype_file = fields.Binary(
        string='Ventor Application Logo File',
        related='company_id.logotype_file',
        readonly=False
    )

    module_outgoing_routing = fields.Boolean(
        string='Outgoing Routing'
    )

    add_barcode_on_view = fields.Boolean(
        string='Show the Location barcode field on the form',
    )

    base_version = fields.Char(
        string='Base Module Version',
        compute='_compute_base_version',
        store=False,
    )

    force_lot_validation_on_inventory_adjustment = fields.Boolean(
        string='Force Lot Validation on Inventory Adjustment',
        readonly=False,
        related='company_id.force_lot_validation_on_inventory_adjustment',
    )

    custom_package_name = fields.Char(
        string='Custom package name',
        config_parameter='ventor_base.custom_package_name',
    )

    @api.depends('company_id')
    def _compute_base_version(self):
        self.env.cr.execute(
            "SELECT latest_version FROM ir_module_module WHERE name='ventor_base'"
        )
        result = self.env.cr.fetchone()
        full_version = result and result[0]
        split_value = full_version and full_version.split('.')
        self.base_version = split_value and '.'.join(split_value[-3:])

    @api.model
    def get_values(self):
        res = super(VentorConfigSettings, self).get_values()

        view_with_barcode = self.env.ref(
            'ventor_base.view_location_form_inherit_additional_barcode',
            raise_if_not_found=False
        )
        if view_with_barcode:
            res['add_barcode_on_view'] = view_with_barcode.active

        return res

    def _set_apply_default_lots(self, previous_group):
        operation_type_ids = self.env['stock.picking.type'].search([])
        group_stock_production_lot = previous_group.get('group_stock_production_lot')

        if (
            group_stock_production_lot != self.group_stock_production_lot
            and not self.group_stock_production_lot
        ):
            operation_type_ids.apply_default_lots = False
            ventor_apply_default_lots = self.env['ventor.option.setting'].search(
                [
                    ('technical_name', '=', 'apply_default_lots'),
                ]
            )
            ventor_apply_default_lots.with_context(
                disable_apply_default_lots=True
            ).set_apply_default_lots_fields(self.group_stock_production_lot)

    def _set_packages_fields(self, previous_group):
        operation_type_ids = self.env['stock.picking.type'].search([])
        group_stock_tracking_lot = previous_group.get('group_stock_tracking_lot')

        if group_stock_tracking_lot != self.group_stock_tracking_lot:
            operation_type_ids.manage_packages = self.group_stock_tracking_lot
            operation_type_ids.show_put_in_pack_button = self.group_stock_tracking_lot
            if not self.group_stock_tracking_lot:
                operation_type_ids.show_put_in_pack_button = self.group_stock_tracking_lot
                operation_type_ids.scan_destination_package = self.group_stock_tracking_lot
                operation_type_ids.confirm_source_package = self.group_stock_tracking_lot
                operation_type_ids.allow_creating_new_packages = self.group_stock_tracking_lot

                ventor_packages_settings = self.env['ventor.option.setting'].search(
                    [
                        (
                            'technical_name',
                            'in',
                            (
                                'confirm_source_package',
                                'scan_destination_package',
                                'manage_packages',
                                'allow_creating_new_packages',
                            ),
                        ),
                    ]
                )
                ventor_packages_settings.with_context(
                    disable_package_fields=True
                ).set_related_package_fields(self.group_stock_tracking_lot)
            if self.group_stock_tracking_lot:
                ventor_packages_settings = self.env['ventor.option.setting'].search(
                    [
                        ('technical_name', '=', 'manage_packages'),
                    ]
                )
                ventor_packages_settings.value = self.env.ref('ventor_base.bool_true')

    def _set_manage_product_owner(self, previous_group):
        operation_type_ids = self.env['stock.picking.type'].search([])
        group_stock_tracking_owner = previous_group.get('group_stock_tracking_owner')

        if group_stock_tracking_owner != self.group_stock_tracking_owner:
            operation_type_ids.manage_product_owner = self.group_stock_tracking_owner

            ventor_owner_settings = self.env['ventor.option.setting'].search(
                [
                    ('technical_name', '=', 'manage_product_owner'),
                ]
            )
            ventor_owner_settings.value = self.env.ref('ventor_base.bool_true') if self.group_stock_tracking_owner else self.env.ref('ventor_base.bool_false')

    def set_values(self):
        previous_group = self.default_get(
            [
                'group_stock_tracking_lot',
                'group_stock_tracking_owner',
                'group_stock_production_lot',
            ]
        )
        res = super(VentorConfigSettings, self).set_values()

        view_with_barcode = self.env.ref('ventor_base.view_location_form_inherit_additional_barcode')
        view_with_barcode.active = self.add_barcode_on_view

        self.sudo()._set_apply_default_lots(previous_group)
        self.sudo()._set_packages_fields(previous_group)
        self.sudo()._set_manage_product_owner(previous_group)
        return res
