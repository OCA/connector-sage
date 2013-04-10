# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
from StringIO import StringIO
import csv
import web
import urllib2
import urllib
import base64
import cStringIO
import tools
from tools.translate import _
from tools.misc import get_iso_codes
import pooler
import time
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
		'formats': fields.char( 'File Format',10),
                'state': fields.selection( ( ('choose','choose'),   # choose date
                     ('get','get'),         # get the file
                   ) ),
		'invoice_ids': fields.many2many('account.invoice', 'sale_order_invoice_export_rel', 'order_id', 'invoice_id', 'Invoices',required=True ,help="This is the list of invoices that have been generated for this sales order. The same sales order may have been invoiced in several times (by line for example)."),
                }
    _defaults = {
                 'state': lambda *a: 'choose',
                }
    def act_cancel(self, cr, uid, ids, context=None):
        #self.unlink(cr, uid, ids, context)
        return {'type':'ir.actions.act_window_close' }


    def act_destroy(self, *args):
        return {'type':'ir.actions.act_window_close' }   

 
    def create_report(self,cr,uid,ids,context={}):
        this = self.browse(cr, uid, ids)[0]
	data = self.read(cr, uid, ids, [], context=context)[0]
	if not data['invoice_ids']:
            raise osv.except_osv(_('Error'), _('You have to select at least 1 Invoice. And try again'))
        
	output = '<Version>''\n'+'"12001"'+','+'"1"''\n'+'</Version>\n\n'
	#Faire le traitement des autres lignes dans les lignes de factures
	pool=pooler.get_pool(cr.dbname)
        line_obj=pool.get('account.invoice')
	if 1==1:
	    for line in line_obj.browse(cr, uid, data['invoice_ids']):
	    #for line in line_obj.browse(cr, uid, ids):
		# tag de debut pour les lignes de factures
		output += '<SalInvoice>''\n'
		#informations sur le client
		customer_name = line.partner_id.name
		oneTimefield ="" or "" 
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
		customer ='"'+customer_name+'"'+','+oneTimefield+',"'+contact_name+'"'+',"'+street1+'"'+',"'+street2+'"'+',"'+city+'"'+',"'+province_state+'"'+',"'+zip_code+'"'+',"'+country+'"'+',"'+phone1+'"'+',"'+mobile+'"'+',"'+fax+'"'+',"'+email+'"'
		#print customer
		#exit(0)
		output += customer.encode('UTF-8')+'\n'
		#informations sur la facture
		no_of_details = str(len(line.abstract_line_ids))
		order_no = "" or ""
		invoice_no = str(line.number)
		if line.date_invoice:
		    entry_date = datetime.strptime(line.date_invoice,"%Y-%m-%d").strftime('%m-%d-%Y')  # date format : mm-dd-yyyy
		else:
		    entry_date = ""
		paid_by_type = str(0) # (between 0 and 3)
		paid_by_source = "" or ""
		total_amount = str(line.amount_total) or ""
		freight_amount = str(0.00) 
		sale_invoice = '"'+no_of_details+'"'+',"'+order_no+'"'+',"'+invoice_no+'"'+',"'+entry_date+'"'+',"'+paid_by_type+'"'+',"'+paid_by_source+'"'+',"'+total_amount+'"'+',"'+freight_amount+'"'
		output += sale_invoice.encode('UTF-8')+'\n'
		product_line_invoice_with_taxe = ""
		#Sale invoice detail lines
		if line.abstract_line_ids:
		    for product in line.abstract_line_ids:
		        item_number = str(product.id)
		        quantity = str(product.quantity)
		    	price = str(product.price_unit)
		    	amount = product.quantity * product.price_unit
			amount = str(round(amount,self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')))
			one_product_invoice = '"'+item_number+'"'+',"'+quantity+'"'+',"'+price+'"'+',"'+amount+'"'
			one_product_invoice = one_product_invoice.encode('UTF-8')
			tax_product_line = ""
			# tax information pour chaque produit
			if product.invoice_line_tax_id:
			    for one_taxe in product.invoice_line_tax_id:
			    	tax_name = one_taxe.name
				if one_taxe.price_include:
				    tax_included =  str(1) # 1=yes,0=No
				else:
				    tax_included =  str(0) # 1=yes,0=No
                            	tax_refundable = str(1) # 1=yes,0=No
                            	tax_rate = str(one_taxe.amount)
                            	tax_amount = str(one_taxe.amount)
			    	tax_product_line += ',"'+tax_name+'"'+',"'+tax_included+'"'+',"'+tax_refundable+'"'+',"'+tax_rate+'"'+',"'+tax_amount+'"'
			    
			    #tax_product_line = tax_product_line[:-1]
			    tax_product_line = tax_product_line.encode('UTF-8')
		     	product_line_invoice_with_taxe += one_product_invoice + tax_product_line+'\n'
			#print product_line_invoice_with_taxe , exit(0)
		output += product_line_invoice_with_taxe
		# tag de fin  pour les lignes de factures
		#output += '</SalInvoice>\n'
		output += '</SalInvoice>\n\n\n'
        #output += '\n' + this.start_date + ',' + this.end_date
	this.formats = 'imp'
	filename = 'export_to_sage50'
	this.name =  "%s.%s" % (filename, this.formats)
        out=base64.encodestring(output)
        return self.write(cr, uid, ids, {'state':'get', 'data':out, 'name':this.name, 'format' : this.formats}, context=context)
        
	
exportsage()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
