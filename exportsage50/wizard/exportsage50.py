# -*- encoding: utf-8 -*-
##############################################################################
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
import web
import base64
import tools
from tools.translate import _
from tools.misc import get_iso_codes
import pooler
from datetime import datetime
import decimal_precision as dp


class exportsage(osv.osv):

    """
    Wizard 
    """
    _name = "exportsage"
    _description = "Create imp file  to export  in sage50"
    _inherit = "ir.wizard.screen"
    _columns = {
        'data': fields.binary('File', readonly=True),
        'name': fields.char('Filename', 20, readonly=True),
        'format': fields.char('File Format', 10),
        'state': fields.selection([('choose', 'choose'), # choose date
                                   ('get', 'get')]),
        'invoice_ids': fields.many2many('account.invoice', 'sale_order_invoice_export_rel', 'order_id', 'invoice_id',
                                        'Invoices', required=True,
                                        help="This is the list of invoices that have been generated for this sales order. The same sales order may have been invoiced in several times (by line for example)."),
    }

    _defaults = {
        'state': lambda *a: 'choose',
    }
    def act_cancel(self, cr, uid, ids, context=None):
        #self.unlink(cr, uid, ids, context)
        return {'type':'ir.actions.act_window_close' }


    def act_destroy(self, *args):
        return {'type':'ir.actions.act_window_close' }   

 
    def create_report(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        this = self.browse(cr, uid, ids)[0]
        data = self.read(cr, uid, ids, [], context=context)[0]

        if not data['invoice_ids']:
            raise osv.except_osv(_('Error'), _('You have to select at least 1 Invoice. And try again'))

        output = '<Version>''\n' + '"12001"' + ',' + '"1"''\n' + '</Version>\n\n'
        #Faire le traitement des autres lignes dans les lignes de factures
        pool = pooler.get_pool(cr.dbname)
        line_obj = pool.get('account.invoice')

        for line in line_obj.browse(cr, uid, data['invoice_ids'], context):
            # tag de debut pour les lignes de factures
            output += '<SalInvoice>''\n'
            #informations sur le client
            costumer_name = line.partner_id.name
            oneTimefield = ""
            contact_name = line.partner_id.address[0].name or ""
            street1 = line.partner_id.address[0].street or ""
            street2 = line.partner_id.address[0].street2 or ""
            city = line.partner_id.address[0].city or ""
            province_state = line.partner_id.address[0].state_id.name or ""
            zip_code = line.partner_id.address[0].zip or ""
            country = line.partner_id.address[0].country_id.name or ""
            phone1 = line.partner_id.address[0].phone or ""
            mobile = line.partner_id.address[0].mobile or ""
            fax = line.partner_id.address[0].fax or ""
            email = line.partner_id.address[0].email or ""
            # ligne de client
            fields = [costumer_name, oneTimefield, contact_name, street1, street2,
                      city, province_state, zip_code, country, phone1, mobile, fax, email
                      ]
            costumer = ','.join(['"%s"' % field for field in fields])
            #print costumer
            #exit(0)
            output += costumer.encode('UTF-8') + '\n'
            #informations sur la facture
            no_of_details = str(len(line.invoice_line))
            order_no = ""
            # Invoice number (Max 20 chars)
            invoice_no = str(line.number)
            # date de la facture
            if line.date_invoice:
                entry_date = datetime.strptime(line.date_invoice, "%Y-%m-%d").strftime('%m-%d-%Y')  # date format : mm-dd-yyyy
            else:
                entry_date = ""
            # Informations sur le type de paiement (between 0 and 3)
            # 0 = pay later , 1 = cash , 2 = cheque , 3 = credit card
            # Selectionner le dernier paiement
            list_id = []
            # Paid by source (20 Chars) : Blank- pay later and cash Cheque number or credit card
            paid_by_source = ""
            if line.payment_ids:
                for oneId in line.payment_ids:
                    list_id.append(oneId.id)
                lastId = max(list_id)
                # acceder à partir du dernier paiement à l'objet account_move_line
                account_move_line_obj = self.pool.get('account.move.line')
                account_move_line = account_move_line_obj.browse(cr, uid, lastId, context=context)
                paiement_type = account_move_line.journal_id.type
                if paiement_type == 'cash':
                    paid_by_type = str(1)
                    paid_by_source = account_move_line.ref
                elif paiement_type == 'bank':
                    paid_by_type = str(2)
                else:
                    paid_by_type = str(0) # default value 0 = pay later

            else:
                paid_by_type = str(0) # default value 0 = pay later
            total_amount = str(line.amount_total) or ""
            freight_amount = "0.0"
            fields_sale_invoice = [no_of_details, order_no, invoice_no, entry_date, paid_by_type,
                                  paid_by_source, total_amount, freight_amount,
                                  ]
            sale_invoice = ','.join(['"%s"' % field_sale_invoice for field_sale_invoice in fields_sale_invoice])
            #sale_invoice = '"' + no_of_details + '"' + ',"' + order_no + '"' + ',"' + invoice_no + '"' + ',"' + entry_date + '"' + ',"' + paid_by_type + '"' + ',"' + paid_by_source + '"' + ',"' + total_amount + '"' + ',"' + freight_amount + '"'
            output += sale_invoice.encode('UTF-8') + '\n'
            product_line_invoice_with_taxe = ""
            #Sale invoice detail lines
            account_invoice_line_obj =self.pool.get('account.invoice.line')
            product_ids = account_invoice_line_obj.search(cr, uid, [('invoice_id','=',line.id)])

            if product_ids:
                for product in account_invoice_line_obj.browse(cr, uid, product_ids):
                    item_number = str(product.name)
                    quantity = str(product.quantity)
                    price = str(product.price_unit)
                    amount = product.quantity * product.price_unit
                    amount = str(round(amount, self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')))
                    fields_one_product_invoice = [item_number, quantity, price, amount]
                    one_product_invoice = ','.join(['"%s"' % field_one_product_invoice for field_one_product_invoice in fields_one_product_invoice])
                    #one_product_invoice = '"' + item_number + '"' + ',"' + quantity + '"' + ',"' + price + '"' + ',"' + amount + '"'
                    one_product_invoice = one_product_invoice.encode('UTF-8')
                    tax_product_line = ""
                    # tax information pour chaque produit
                    if product.invoice_line_tax_id:
                        for one_taxe in product.invoice_line_tax_id:
                            tax_name = one_taxe.description # or one_taxe.description or one_taxe.name
                            if one_taxe.price_include:
                                tax_included = str(1) # 1=yes,0=No
                            else:
                                tax_included = str(0) # 1=yes,0=No
                            tax_refundable = str(1) # 1=yes,0=No
                            tax_rate = str(one_taxe.amount)
                            tax_amount = str(one_taxe.amount)
                            fields_tax_product_line = [tax_name, tax_included, tax_refundable, tax_rate, tax_amount,
                                                       ]
                            tax_product_line = ',' + ','.join(['"%s"' % field_tax_product_line for field_tax_product_line in fields_tax_product_line])
                            #tax_product_line += ',"' + tax_name + '"' + ',"' + tax_included + '"' + ',"' + tax_refundable + '"' + ',"' + tax_rate + '"' + ',"' + tax_amount + '"'

                        #tax_product_line = tax_product_line[:-1]
                        tax_product_line = tax_product_line.encode('UTF-8')
                    product_line_invoice_with_taxe += one_product_invoice + tax_product_line + '\n'
                #print product_line_invoice_with_taxe , exit(0)

                output += product_line_invoice_with_taxe
            # tag de fin  pour les lignes de factures
            #output += '</SalInvoice>\n'
            output += '</SalInvoice>\n\n\n'
        #output += '\n' + this.start_date + ',' + this.end_date
        this.format = 'imp'
        filename = 'export_to_sage50'
        this.name = "%s.%s" % (filename, this.format)
        out = base64.encodestring(output)
        self.write(cr, uid, ids, {'state':'get', 'data':out, 'name':this.name, 'format' : this.format}, context=context)
        
exportsage()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
