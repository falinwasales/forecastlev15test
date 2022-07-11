odoo.define('forecastle_module.SalePortalSidebar', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var PortalSidebar = require('sale.SalePortalSidebar');

publicWidget.registry.SalePortalSidebar.include({
    events: {
        'change select[name="shipper_id"]': '_adaptShipperInfoForm',
        'change select[name="consignee_id"]': '_adaptConsigneeInfoForm',
        'change select[name="notify_id"]': '_adaptNotifyInfoForm',
        'change select[name="commodity_type"]': '_onCommodityTypeChange',
        'change select[name="related_booking_party"]': '_onExistingChange',
        'click .o_contact_delete': '_deleteContact',
    },

    /**
     * @constructor
     */
    start: function () {
        console.log('================================================= JALAN BABI CASTLE')
        var def = this._super.apply(this, arguments);
        this.initial_shipper_id = false
        this.initial_consignee_id = false
        this.initial_notify_id = false
        this._adaptShipperInfoForm();
        this._adaptConsigneeInfoForm();
        this._adaptNotifyInfoForm();
        this._adaptContainerInfoForm();
        this._adaptcontact();
        return def;
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @private
     */

    _adaptShipperInfoForm: function () {
        console.log('================================================== TEST')
        var $shipper_id = this.$('select[name="shipper_id"]');
        console.log(shipper_id)
        if($shipper_id.find(":selected")[0]){
            if($shipper_id.find(":selected")[0].attributes[1].value){
                var shipper_value = $shipper_id.find(":selected")[0].attributes[1].value;
                var shipper_address = this.$('.shipper-address')
                if (shipper_value){
                    // Need to check first if there is a change between selected shipper and from the backend
                    if (this.initial_shipper_id){
                        this._rpc({
                            model: 'res.partner',
                            method: 'get_address',
                            args: [parseInt(shipper_value)]
                        }).then(function (result) {
                            shipper_address.val(result)
                        });
                    }else{
                        this.initial_shipper_id = shipper_value;
                    }
                }
            }
        }
    },
    _adaptConsigneeInfoForm: function () {
        var $consignee_id = this.$('select[name="consignee_id"]');
        if($consignee_id.find(":selected")[0]){
            if($consignee_id.find(":selected")[0].attributes[1].value){
                var consignee_value = $consignee_id.find(":selected")[0].attributes[1].value;
                var consignee_address = this.$('.consignee-address')
                if (consignee_value){
                    // Need to check first if there is a change between selected shipper and from the backend
                    if (this.initial_consignee_id){
                        this._rpc({
                            model: 'res.partner',
                            method: 'get_address',
                            args: [parseInt(consignee_value)]
                        }).then(function (result) {
                            consignee_address.val(result)
                        });
                    }else{
                        this.initial_consignee_id = consignee_value;
                    }
                }
            }
        }
    },
    _adaptNotifyInfoForm: function () {
        var $notify_id = this.$('select[name="notify_id"]');
        if($notify_id.find(":selected")[0]){
            if($notify_id.find(":selected")[0].attributes[1]){
                var notify_value = $notify_id.find(":selected")[0].attributes[1].value;
                var notify_address = this.$('.notify-address')
                if (notify_value){
                    // Need to check first if there is a change between selected shipper and from the backend
                    if (this.initial_notify_id){
                        this._rpc({
                            model: 'res.partner',
                            method: 'get_address',
                            args: [parseInt(notify_value)]
                        }).then(function (result) {
                            notify_address.val(result)
                        });
                    }else{
                        this.initial_notify_id = notify_value;
                    }
                }
            }
        }
    },
    _adaptContainerInfoForm: function () {
        var $commodity_type = this.$('select[name="commodity_type"]');
        var commodity_typeText = $commodity_type.find(":selected").text();
        if (commodity_typeText.includes("Standard")){
            this.$('.container-imdg').hide()
            this.$('.container-ems').hide()
            this.$('.container-pg-class').hide()
            this.$('.container-un').hide()
        }else{
            this.$('.container-imdg').show()
            this.$('.container-ems').show()
            this.$('.container-pg-class').show()
            this.$('.container-un').show()
        }
    },
    _adaptcontact: function () {
        var related_booking_party = this.$('select[name="related_booking_party"]');
        var related_booking_partyText = related_booking_party.find(":selected").text();
        var related_booking_partyText_2 = related_booking_party.find(":selected");
        if (related_booking_partyText_2[0]){
            if(related_booking_partyText_2[0].attributes[3]){
                var contact = related_booking_partyText_2[0].attributes[3].value
                var re_contact = contact.replace(/\D/g, '')
                var contact_fix = parseInt(re_contact)
                var name = this.$('.contact-name')
                var sreet = this.$('.contact-street')
                var button = this.$('.o_contact_delete')
                this._rpc({
                            model: 'res.partner',
                            method: 'get_address',
                            args: [contact_fix]
                        }).then(function (result) {
                            if (related_booking_partyText == ''){
                                name.val('');
                                sreet.val('');
                                button.hide();
                            }else{
                                name.val(related_booking_partyText);
                                sreet.val(result);
                                button.show();
                        }
                });
            }
        }
    },

    _deleteContact: function (e) {
        var related_booking_party = this.$('select[name="related_booking_party"]');
        var related_booking_party_selected = related_booking_party.find(":selected");
        var contact = related_booking_party_selected[0].attributes[3].value
        var re_contact = contact.replace(/\D/g, '')
        var contact_id = parseInt(re_contact)
        var sale = this.target.attributes.class.ownerDocument.location.pathname
        var sale_remove_str = sale.replace(/\D/g, '')
        var sale_id = parseInt(sale_remove_str)
        this._rpc({
                    model: 'res.partner',
                    method: 'unlink_address',
                    args: [contact_id, sale_id]
                }).then(function (result) {
                    location.reload();
            });
    },


    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onCommodityTypeChange: function () {
        this._adaptContainerInfoForm();
    },
    _onExistingChange: function () {
        this._adaptcontact();
    },
});
});
