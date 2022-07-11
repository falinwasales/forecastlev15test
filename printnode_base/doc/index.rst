Contents
********

|

* `Steps for PrintNode`_
* `Steps for Odoo`_
* `Print Action Button Configuration`_
* `FAQ`_
* `Troubleshooting`_
* `Change Log`_

|

==========================
 Quick configuration guide
==========================

|

Steps for PrintNode
###################

|

1. Sign up for `PrintNode <https://www.printnode.com/en>`_ to create a new account and generate an API key.
2. To use PrintNode you need to install and run the `PrintNode Client <https://www.printnode.com/en/download>`_ software on a computer that has access to all your printers in your network and is connected to the internet. (By the default Pricing Plan PrintNode supports installation of the client software on three different computers, but you can add more devices at any time.)
3. Open the API menu and copy `your API key <https://app.printnode.com/app/apikeys>`_ for later use.

|

.. image:: images/image11.png
   :width: 800px

|

Steps for Odoo
##############

|

4. Install the Odoo PrintNode app on your Odoo server. `How to install in Odoo.sh <https://youtu.be/p4KE10FbYk0>`_
5. Go to PrintNode app > Configuration > Accounts > Click CREATE > Insert your API key copied from earlier and click "save".

|

.. image:: images/image10.png
   :width: 800px

|

6. Click on the "Import printers" button to get all printers from your PrinNode app.
7. Go to PrintNode settings and set up default printers (Don't forget to set up a shipping label if needed)

|

.. image:: images/image19.png
   :width: 800px

|

8. Go to user preferences, set up the default printers, and click in the "Print via PrintNode" checkbox (if the checkbox “Print via PrintNode” is set, then all documents will be auto-forwarded to the printer instead of downloading in PDF).

|

.. image:: images/image7.png
   :width: 800px

|

9. That's it, you can now print directly on your default printers. Try to print any document, and make sure your printer is switched on!

|

.. image:: images/image9.png
   :width: 800px

|

TEST ON OUR SERVER > https://odoo.ventor.tech

Our Demo server is recreated every day at 12.00 AM (UTC). All your manually entered data will be deleted at this time.

|

Print Action Button Configuration
#################################

|

.. image:: images/image23.jpeg
   :width: 800px

|

If you need to set up an additional condition for print action buttons (e.g. print delivery slip only in the Delivery zone, or for deliveries shipped to particular countries) you should define Domain

|

.. image:: images/image17.png
   :width: 800px

|

How to set up domains:
----------------------

|

.. image:: images/image20.png
   :width: 800px

|

Leave the field "Printer" blank for print action button in case you need to print reports on user's printer (set up in user preferences)

|

.. image:: images/image21.png
   :width: 800px

|

FAQ
###

|

*1. Does every computer in the company that needs to print, need to install the nodeprint client app on the local computer? Or only the computers where the printer is physically attached?*

|

It's enough to have only one machine that has access to all needed printers.
We even recommend to set-up a separate PC for this. E.g. we configured a Raspberry PI 4 in our office for printing purposes.
It's absolutely doesn't matter where are the printers and connected to a local or external network. If the printnode client sees them, you can print.

|

*2. Are there any limitations on the side of hosting Odoo? We use Docker/Kubernetes based deployments. Are you aware of any issues with such environments?*

|

No issues if your Odoo server has internet access.

|

*3. I see you use cups as printer server. How does this work on odoo.sh Do we have to make a vpn connection between odoo.sh and the warehouse?*

|

No need to make VPN connection. You will just need to install special PrintNode Client on any local machine in your network with printers. CUPS will be needed only if this machine will be linux based.

|

*4. Is this similar to Odoo's IOT app?  Can you explain the differences?*

|

The main differences are:
    - Odoo IoT requires additional hardware. For subscription-based pricing. You can use Odoo direct print app with any machine that has access to all needed printers.
    - Odoo IoT works only with Odoo Enterprise.
    - Odoo direct print can print documents automatically (Delivery slips, shipping labels, other reports...).
    - Odoo direct print works with any remote or local (USB, Wi-Fi, Bluetooth) printer.

|

Troubleshooting
###############

|

If the system downloads reports instead of printing them, please check that the "Print via PrintNode" checkbox has been ticked:

|

.. image:: images/image14.png
   :width: 800px

|

Change Log
##########

|

* 1.9.3 (2021-08-23)
    - Added "Print Scenario" to print document after Purchase order confirmation
    - Added "Print Scenario" to print "Receipt Document" after Purchase Order Validation

* 1.9.2 (2021-08-13)
    - Added possibility to exclude particular report from printing in "Print Settings"

* 1.9.1 (2021-07-29)
    - Fixed error in module installation with other modules that are changing user's form view
    - Fixed regression issue with impossibility to quick print product label via wizard
    - Fixed issue with settings not properly working in multi-company environment

* 1.9.0 (2021-07-27)
    - Download Printer Bins Information (Paper Trays).
    - Allow to define Printer Bin (Tray) to be used in all places (Print Actions, Print Scenarios, User Rules)
    - When deleting account - delete all related objects (Computers, Printers, Print Jobs, User Rules, Printer Bins)

* 1.8.1 (2021-07-20)
    - Switching off "Print via Printnode" on user or company also should switch off auto-printing of shipping label on DO Validation

* 1.8.0 (2021-07-14)
    - Added possibility to print Package Document together with the Shipping Label
    - Added Print Scenario to Print all Packages after Transfer Validation

* 1.7.3 (2021-07-13)
    - Fix issue with auto-test for purchase order flow and user access rights

* 1.7.2 (2021-07-08)
    - Fix issue with printing multiple documents using scenarios with the same action

* 1.7.1 (2021-06-30)
    - Fix issue with automatic Shipping Label printing from attachments via "Print Last Shipping Label" button on Delivery Order
    - Adding possibility to enable debug logging on the account to log requests that are sent to PrintNode (needed to communicate with support)

* 1.7 (2021-06-14)
    - When automatic printing is enabled in User Preferences, display near "Print" menu new dropdown "Download" that will allow to Download reports as in Odoo standard.

* 1.6.3 (2021-06-08)
    - Method _create_backorder() must return a recordset like the original method does, so that other modules could extend it as well.

* 1.6.2 (2021-06-05)
    - Fixed issue with download of printers when there is big amount of printers in Printnode account.
    - When deleting account also delete inactive computers and printers

* 1.6.1 (2021-05-31)
    - Fixed issue that makes module incompatible with modules redefining Controller for report download (e.g. report_xlsx).

* 1.6 (2021-04-16)
    - Added  possibility to define Universal Print Attachments Wizard for any model in the Odoo.
    - (Experimental) Added settings to allow auto-printing of shipping labels from attachments. To support shipping carriers implemented not according to Odoo standards.
    - Fix printing error when sending to PrintNode many documents at the same time.

* 1.5.2 (2021-03-26)
    - Added print scenarios to print "Lot labels" or "Product Labels" in real time when receiving items.
      It allows either to print single label (to stick on box) OR multiple labels equal to quantity of received items

* 1.5.1 (2021-03-13)
    - Fixed an issue with Report Download controller interruption
    - Fixed an issue with printing document with scenarios for different report model

* 1.5 (2021-02-25)
    - Removed warning with Unit tests when installing module on Odoo.sh.
    - Added new scenario: print product labels for validated transfers.
    - Added new scenario: print picking document after sale order confirmation.

* 1.4.2 (2021-01-13)
    - Added possibility to view the number of prints consumed from the printnode account (experimental).

* 1.4.1 (2021-01-12)
   - Updating the "printed" flag on stock.picking model after Print Scenario execution.

* 1.4 (2020-12-21)
    - Added possibility to define number of copies to be printed in "Print Action Button" menu.
    - Added Print Scenarios which allows to print reports on pre-programmed actions.

* 1.3.1 (2020-11-10)
    - Added constraints not to allow creation of not valid "Print Action Buttons" and "Methods".
    - On product label printing wizard pre-select printer in case only 1 suitable was found.

* 1.3 (2020-10-09)
    - Added possibility to print product labels while processing Incoming Shipment into your Warehouse.
      Also you can mass print product labels directly from individual product or product list.
    - Show info message on User Preferences in case there are User Rules that can redefine Default user Printer.
    - Added examples to Print Action menu for some typical use cases for Delivery Order and Sales Order printing.

* 1.2.1 (2020-10-07)
    - When direct-printing via Print menu, there is popup message informing user about successful printing.
      Now this message can be disabled via Settings.
    - Fixed issue with wrong Delivery Slip printing, after backorder creation.

* 1.2 (2020-07-28)
    -  Make Printer non-required in "Print action buttons" menu. If not defined, than printer will be selected
       based on user or company printer setting.
    -  Added Support for Odoo Enterprise Barcode Interface. Now it is compatible with "Print action buttons" menu.
    -  "Print action buttons" menu now allows to select filter for records, where reports should be auto-printed.
       E.g. Print Delivery Slip only for Pickings of Type = Delivery Order.

* 1.1 (2020-07-24)
    -  Added Support for automatic/manual printing of Shipping Labels.
       Supporting all Odoo Enterprise included Delivery Carries (FedEx, USPS, UPS, bpost and etc.).
       Also Supporting all custom carrier integration modules that are written according to Odoo Standards.

* 1.0 (2020-07-20)
    - Initial version providing robust integration of Odoo with PrintNode for automatic printing.

|
