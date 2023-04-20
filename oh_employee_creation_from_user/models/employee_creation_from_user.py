# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    employee_id = fields.Many2one('hr.employee',
                                  string='Related Employee', ondelete='restrict', auto_join=True,
                                  help='Employee-related data of the user')

    @api.model_create_multi
    def create(self, vals_list):
        """This code is to create an employee while creating an user."""
        users = super(ResUsersInherit, self).create(vals_list)
        for user in users:
            employee = self.env['hr.employee'].sudo().create(
                {'name': user.name,
                 'user_id': user.id,
                 #'address_home_id': user.partner_id.id
                 })
        return users
