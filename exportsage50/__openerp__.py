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

{
    'name': 'Export to Sage50',
    'version': '8.0.1.0.0',
    "category": 'Accounting & Finance',
    'complexity': "easy",
    'description': """
French version below

Export accounting data from OpenErp to Sage50.
====================================
 Export accounting data from OpenErp to Sage50. The exportation generates the imp file to import in Sage50.


Documentation : layout of the import file (.IMP)
====================================
A PDF document (in the /doc repository) gives more details about the .IMP file layout that can be imported
into Sage 50.This document is part of the Sage 50 SDK (Software Development Kit) available for download at
the following address : http://na.sage.com/sage-simply-accounting/lp/partners/sdk/?isnow=ssa.



Sage 50: After creating .IMP file
====================================
Solution:
Importing purchase invoices, purchase quotes, sales invoices and sales orders into Sage 50
How to import purchase invoices, purchase quotes, sales invoices and sales orders?
You can import purchase invoices, purchase quotes, sales invoices and sales orders into Sage 50.
The transaction(s) details should be in a text file with extension .IMP.


After you have created the .IMP file, you can import the transaction(s) into Sage 50 by following these steps:
(Account information is not included in the .IMP format because when importing the file, you will receive
a pop-up screen to ask you "Select an Account to match".)

From the Home Window, go to File, Import/Export
Click on Import Transactions (the Import Transactions Wizard appears)
Select on 'Import purchase invoices, purchase quotes, sales invoices, sales orders or time slips' and click Next
You can now create a backup of your file
Click Next
Click on Browse and select the .IMP file previously created
If the customer (or vendor) in the transaction(s) you are trying to import does not exist in the Sage 50 company,
you will get a new window asking you if you want to add this customer (or vendor), or if you want to select
another customer (or vendor) from the existing ones
You will also get a similar window if the import file uses an inventory item which does not exist in Sage 50.
You will see a summary of the imported transactions, click OK and then Finish.
If you got any errors importing the data, open the .IMP file in Notepad and use the attached .PDF document
to verify the file format. Once the errors have been corrected, you can try the import again.
Note: View KB25664 for information about some possible errors when importing .IMP file.
Sage Business Care plan does NOT include support for SDK. Please, contact one of our partners website
for further assistance.

Possible errors when importing purchase invoices, purchase quotes, sales invoices and/or sales orders
====================================
Questions and Answers
Import started... Errors occurred while importing.
Line x does not contain compatible tax information.
Invalid date. The date must be between <date1> and <date2>.


A: These are the possible reasons for getting any of these error messages when importing transactions
into Simply Accounting:

- The import file (extension .IMP) you are using does not have the proper format.
  Refer to the KB article 25659 for more information about the format of the import file.

- The transaction type is not enabled in the Simply Accounting company. To enable the feature, from the Home Window
in Simply Accounting, go to Setup, Settings, Company, Features, make sure the type of transaction you want to import
is checked

- The dates in the import file do not match the fiscal year dates in Simply Accounting.
  Open the import file in Notepad and make the necessary changes


Exportation des données comptables de OpenERP vers Sage50.
==============================================
Ce module exporte des données comptables de OpenERP vers Sage50. Le module génére un fichier imp file qui peut
être importé dans Sage50.

Documentation : Format du fichier à importer (.IMP)
====================================
Un document .PDF (dans le répertoire /doc) donne plus de détails sur le format du fichier .IMP qui peut être
importé dans Sage 50. Ce document fait parti du Kit de développement - SDK de Sage 50  qui peut-être téléchargé
à l'adresse suivante : http://na.sage.com/sage-simply-accounting/lp/partners/sdk/?isnow=ssa.

Guide d'utilisation export Sage 50
========================================
Comment exporter les données comptables à partir d'OpenERP?
Un manuel d'utilisation est disponible dans le répertoire /doc du module.

    """,
    "author": "Gestion-Ressources,Odoo Community Association (OCA)",
    "website": "http://www.gestion-ressources.com",
    "license": "AGPL-3",
    'images': [],
    'depends': ['account'],
    'update_xml': [
        'wizard/exportsage50.xml',
        'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'test':[],
    'installable': True,
    'auto_install': False,
    'certificate': '',
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
