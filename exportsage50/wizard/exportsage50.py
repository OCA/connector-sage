# -*- encoding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Gestion-Ressources (<http://www.gestion-ressources.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import fields, orm
import base64
from openerp.tools.translate import _
import pooler
from datetime import datetime
import unicodedata


class exportsage(orm.Model):
    _name = "exportsage"
    _description = "Create imp file  to export  in sage50"
    _columns = {
        'data': fields.binary('File', readonly=True),
        'name': fields.char('Filename', 20, readonly=True),
        'format': fields.char('File Format', 10),
        'state': fields.selection([('choose', 'choose'),
                                   ('get', 'get')]),
        'invoice_ids': fields.many2many('account.invoice', 'sale_order_invoice_export_rel', 'order_id', 'invoice_id',
                                        'Invoices', required=True,
                                        help="This is the list of invoices that have been generated "
                                             "for this sales order. The same sales order may have been invoiced "
                                             "in several times (by line for example)."),
    }

    _defaults = {
        'state': lambda *a: 'choose',
    }

    def act_cancel(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}

    def act_destroy(self, *args):
        return {'type': 'ir.actions.act_window_close'}

    def create_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        this = self.browse(cr, uid, ids, context=context)[0]
        data = self.read(cr, uid, ids, [], context=context)[0]

        if not data['invoice_ids']:
            raise orm.except_orm(_('Error'), _('You have to select at least 1 Invoice. And try again'))

        output = '<Version>''\n' + '"12001"' + ',' + '"1"''\n' + '</Version>\n\n'
        # Do the treatment of other lines in the invoice lines
        pool = pooler.get_pool(cr.dbname)
        line_obj = pool.get('account.invoice')
        account_move_line_obj = self.pool.get('account.move.line')
        account_invoice_line_obj = self.pool.get('account.invoice.line')
        decimal_precision_obj = self.pool.get('decimal.precision')

        for line in line_obj.browse(cr, uid, data['invoice_ids'], context=context):
            # start tag for invoice lines
            output += '<SalInvoice>''\n'
            #informations sur le client
            costumer_name = line.partner_id.name
            onetimefield = ""
            contact_name = line.partner_id.name or ""
            street1 = line.partner_id.street or ""
            street2 = line.partner_id.street2 or ""
            city = line.partner_id.city or ""
            province_state = line.partner_id.state_id.name or ""
            zip_code = line.partner_id.zip or ""
            country = line.partner_id.country_id.name or ""
            phone1 = line.partner_id.phone or ""
            mobile = line.partner_id.mobile or ""
            fax = line.partner_id.fax or ""
            email = line.partner_id.email or ""
            # Customer line
            fields = [costumer_name, onetimefield, contact_name, street1, street2,
                      city, province_state, zip_code, country, phone1, mobile, fax, email
                      ]
            costumer = ','.join(['"%s"' % field for field in fields])
            output += costumer.encode('UTF-8') + '\n'
            # Invoice informations
            no_of_details = str(len(line.invoice_line))
            order_no = ""
            # Invoice number (Max 20 chars)
            invoice_no = str(line.number)
            # Get invoice date
            entry_date = datetime.strptime(line.date_invoice, "%Y-%m-%d").strftime('%m-%d-%Y')\
                if line.date_invoice else ""
            # Type of payment (between 0 and 3)
            # 0 = pay later , 1 = cash , 2 = cheque , 3 = credit card
            # Select last payment
            list_id = []
            # Paid by source (20 Chars) : Blank- pay later and cash Cheque number or credit card
            paid_by_source = ""
            if line.payment_ids:
                lastId = max(line.payment_ids).id
                for oneId in line.payment_ids:
                    list_id.append(oneId.id)
                lastId = max(list_id)
                # access from the last payment account_move_line object
                account_move_line = account_move_line_obj.browse(cr, uid, lastId, context=context)
                paiement_type = account_move_line.journal_id.type
                if paiement_type == 'cash':
                    paid_by_type = str(1)
                    paid_by_source = account_move_line.ref
                elif paiement_type == 'bank':
                    paid_by_type = str(2)
                else:
                    paid_by_type = str(0)  # default value 0 = pay later
            else:
                paid_by_type = str(0)  # default value 0 = pay later
            total_amount = str(line.amount_total) or ""
            freight_amount = "0.0"
            fields_sale_invoice = [no_of_details, order_no, invoice_no, entry_date, paid_by_type,
                                   paid_by_source, total_amount, freight_amount]
            sale_invoice = ','.join(['"%s"' % one_field for one_field in fields_sale_invoice])
            output += sale_invoice.encode('UTF-8') + '\n'
            product_line_invoice_with_tax = ""
            #Sale invoice detail lines
            product_ids = account_invoice_line_obj.search(cr,
                                                          uid,
                                                          [('invoice_id', '=', line.id)],
                                                          context=context)

            if product_ids:
                for product in account_invoice_line_obj.browse(cr,
                                                               uid,
                                                               product_ids,
                                                               context=context):
                    item_number = unicode(product.name, "utf8", "replace") \
                        if isinstance(product.name, str) else unicodedata.normalize('NFD', product.name)
                    quantity = str(product.quantity)
                    price = str(product.price_unit)
                    amount = product.quantity * product.price_unit
                    amount = str(round(amount, decimal_precision_obj.precision_get(cr, uid, 'Account')))
                    fields_one_product_invoice = [item_number, quantity, price, amount]
                    one_product_invoice = ','.join(['"%s"' % field_one_product_invoice
                                                    for field_one_product_invoice in fields_one_product_invoice])
                    one_product_invoice = one_product_invoice.encode('UTF-8')
                    tax_product_line = ""
                    # Tax information for each product
                    if product.invoice_line_tax_id:
                        for one_tax in product.invoice_line_tax_id:
                            tax_name = one_tax.description  # or one_tax.description or one_tax.name
                            # 1=yes, 0=No
                            tax_included = str(1) if one_tax.price_include else str(0)
                            tax_refundable = str(1)  # 1=yes, 0=No
                            tax_rate = str(one_tax.amount)
                            tax_amount = str(one_tax.amount)
                            fields_tax_product_line = [tax_name, tax_included, tax_refundable, tax_rate, tax_amount, ]
                            tax_product_line = ',' + ','.join(['"%s"' % one_tax_field
                                                               for one_tax_field in fields_tax_product_line])
                        tax_product_line = tax_product_line.encode('UTF-8')
                    product_line_invoice_with_tax += one_product_invoice + tax_product_line + '\n'
                output += product_line_invoice_with_tax
            # End of invoice lines
            output += '</SalInvoice>\n\n\n'
        this.format = 'imp'
        filename = 'export_to_sage50'
        this.name = "%s.%s" % (filename, this.format)
        out = base64.encodestring(output)
        self.write(cr, uid, ids, {'state': 'get', 'data': out, 'name': this.name,
                                  'format': this.format}, context=context)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'exportsage',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
