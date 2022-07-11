odoo.define('forecastle_module.root', function (require) {
'use strict';

const ajax = require('web.ajax');
const {_t} = require('web.core');
var Dialog = require('web.Dialog');
const KeyboardNavigationMixin = require('web.KeyboardNavigationMixin');
const session = require('web.session');
var WebsiteRoot = require('website.root');

WebsiteRoot.WebsiteRoot.include({
    _onModalShown: function (ev) {
        var button = $(ev.relatedTarget) // Button that triggered the modal

        // For Import
        var modalimportcontainerinfo_id = button.data('modalimportcontainerinfo_id')
            $(ev.target).find('.import-container-line').val(modalimportcontainerinfo_id);
        var modalimportcontainerproductname = button.data('modalimport-container-product-name')
            $(ev.target).find('.import-container-product').text(modalimportcontainerproductname);
        var modalimportquantity = button.data('modalimportquantity')
            $(ev.target).find('.import-quantity').text(modalimportquantity);
        var modalimportdatearrival = button.data('modalimportdatearrival')
            $(ev.target).find('.import-date-arrival').text(modalimportdatearrival);
        var modalimportfreetime = button.data('modalimportfreetime')
        if (modalimportfreetime){
            if (modalimportfreetime == 'day7'){
                $(ev.target).find('.import-free-time').text('7 Days');
            }
            if (modalimportfreetime == 'day14'){
                $(ev.target).find('.import-free-time').text('14 Days');
            }
            if (modalimportfreetime == 'day21'){
                $(ev.target).find('.import-free-time').text('21 Days');
            }
        }

        var modalimportlastdate = button.data('modalimportlastdate')
            $(ev.target).find('.import-last-date').text(modalimportlastdate);
        var modalimportextend_do = button.data('modalimportextend_do')
            $(ev.target).find('.import-extend-do').val(modalimportextend_do);
            $(ev.target).find('.import-extend-do-text').text(modalimportextend_do);
        var modalimportdetentiondays = button.data('modalimportdetentiondays')
            $(ev.target).find('.import-detention-days').text(modalimportdetentiondays);
        var modalimportgatein = button.data('modalimportgatein')
            if (modalimportgatein){
                $(ev.target).find('.import-extend-do-text').show()
                $(ev.target).find('.import-extend-do').hide()
            } else {
                $(ev.target).find('.import-extend-do-text').hide()
                $(ev.target).find('.import-extend-do').show()
            }


        var modalimportnonslab = button.data('modalimportnonslab')
            $(ev.target).find('.import-non-slab').text(modalimportnonslab);
        if (modalimportnonslab == undefined) {
            $(ev.target).find('.import-non-slab').text('0.0');
        }
        var modalimportslab1 = button.data('modalimportslab1')
            $(ev.target).find('.import-slab1').text(modalimportslab1);
        if (modalimportslab1 == undefined) {
            $(ev.target).find('.import-slab1').text('0.0');
        }
        var modalimportslab2 = button.data('modalimportslab2')
            $(ev.target).find('.import-slab2').text(modalimportslab2);
        if (modalimportslab2 == undefined) {
            $(ev.target).find('.import-slab2').text('0.0');
        }

        var modalimportslab3 = button.data('modalimportslab3')
            $(ev.target).find('.import-slab3').text(modalimportslab3);
        if (modalimportslab3 == undefined) {
            $(ev.target).find('.import-slab3').text('0.0');
        }

        var modalimportslab4 = button.data('modalimportslab4')
            $(ev.target).find('.import-slab4').text(modalimportslab4);
        if (modalimportslab4 == undefined) {
            $(ev.target).find('.import-slab4').text('0.0');
        }

        var modalimportotaldetentiondeposit = button.data('modalimportotaldetentiondeposit')
            $(ev.target).find('.import-total-detention-deposit').text(modalimportotaldetentiondeposit);
        if (modalimportotaldetentiondeposit == undefined) {
            $(ev.target).find('.import-total-detention-deposit').text('0.0');
        }

        // End Of Import

        // on change Payment Term
        var modalchargeinfo_payment_term = button.data('modalchargeinfo_payment_term')
        if (modalchargeinfo_payment_term){
            if (modalchargeinfo_payment_term == 'prepaid'){
                $(ev.target).find('.prepaid').attr("selected","selected");
            }else{
                $(ev.target).find('.collect').attr("selected","selected");
            }
        }
        var modalchargeinfo_bill_to_id = button.data('modalchargeinfo_bill_to_id')
            $(ev.target).find('.bill_to_id').val(modalchargeinfo_bill_to_id);

        var modalchargeinfo_id = button.data('modalchargeinfo_id')
            $(ev.target).find('.charges-line').val(modalchargeinfo_id);

        var modalchargeinfo_name = button.data('modalchargeinfo_name')
            $(ev.target).find('.chargeinfo-name').text(modalchargeinfo_name);

        // On Container Qty
        var modalcontainerline_name = button.data('modalcontainerline_name')
        if (modalcontainerline_name){
        	// Change the Container Name
            $(ev.target).find('.container-quantity').text(modalcontainerline_name);
            // Change the hidden value of set_id
            var modalcontainerline_id = button.data('modalcontainerline_id')
            $(ev.target).find('.sale-line').val(modalcontainerline_id);
            // Change the initial value of qty
            var modalcontainerline_setqty = button.data('modalcontainerline_setqty')
            $(ev.target).find('.set-qty').val(modalcontainerline_setqty);
        }
        // On Container Info
        var modalcontainerinfo_name = button.data('modalcontainerinfo_name')
        if (modalcontainerinfo_name){
            // Change the Container Name
            $(ev.target).find('.container-name').text(modalcontainerinfo_name);
            // Change the hidden value of container
            var modalcontainerinfo_id = button.data('modalcontainerinfo_id')
            $(ev.target).find('.container-line').val(modalcontainerinfo_id);
            // Change the Cargo Type
            var modalcontainerinfo_commodity_type = button.data('modalcontainerinfo_commodity_type')
            if (modalcontainerinfo_commodity_type == 'dg'){
                $(ev.target).find('.cargo_dg').attr("selected","selected");
            }else{
                $(ev.target).find('.cargo_std').attr("selected","selected");
                $(ev.target).find('.container-imdg').hide();
                $(ev.target).find('.container-ems').hide();
                $(ev.target).find('.container-pg-class').hide()
                $(ev.target).find('.container-un').hide();
            }
            // Change Container Catgeory
            var modalcontainerinfo_container_categ = button.data('modalcontainerinfo_container_categ')
            if (modalcontainerinfo_container_categ == 'soc'){
                $(ev.target).find('.soc').attr("selected","selected");
            }else{
                $(ev.target).find('.coc').attr("selected","selected");
            }
            // Change pg class
            var modalcontainerinfo_pgclass = button.data('modalcontainerinfo_pgclass')
            $(ev.target).find('.container-pg-class').val(modalcontainerinfo_pgclass);
            // Change the Gross Weight
            var modalcontainerinfo_gross = button.data('modalcontainerinfo_gross')
            $(ev.target).find('.container-gross').val(modalcontainerinfo_gross);
            // Change the Net
            var modalcontainerinfo_nett = button.data('modalcontainerinfo_nett')
            $(ev.target).find('.container-net').val(modalcontainerinfo_nett);
            // Change the Measure
            var modalcontainerinfo_measure = button.data('modalcontainerinfo_measure')
            $(ev.target).find('.container-measure').val(modalcontainerinfo_measure);
            // Change the IMDG
            var modalcontainerinfo_imdg_class = button.data('modalcontainerinfo_imdg_class')
            $(ev.target).find('.container-imdg').val(modalcontainerinfo_imdg_class);
            // Change the EMS
            var modalcontainerinfo_ems_number = button.data('modalcontainerinfo_ems_number')
            $(ev.target).find('.container-ems').val(modalcontainerinfo_ems_number);
            // Change the UN
            var modalcontainerinfo_un = button.data('modalcontainerinfo_un')
            $(ev.target).find('.container-un').val(modalcontainerinfo_un);
            // Change the Lenght
            var modalcontainerinfo_lenght = button.data('modalcontainerinfo_lenght')
            $(ev.target).find('.container-lenght').val(modalcontainerinfo_lenght);
            // Change the Height
            var modalcontainerinfo_height = button.data('modalcontainerinfo_height')
            $(ev.target).find('.container-height').val(modalcontainerinfo_height);
            // Change the Width
            var modalcontainerinfo_width = button.data('modalcontainerinfo_width')
            $(ev.target).find('.container-width').val(modalcontainerinfo_width);
            // Change the Dimension
            var modalcontainerinfo_dimension = button.data('modalcontainerinfo_dimension')
            $(ev.target).find('.container-dimension').val(modalcontainerinfo_dimension);
            // Change the Temp
            var modalcontainerinfo_temp = button.data('modalcontainerinfo_temp')
            $(ev.target).find('.container-temp').val(modalcontainerinfo_temp);
            // Change Cont No
            var modalcontainerinfo_seal = button.data('modalcontainerinfo_seal')
            $(ev.target).find('.container-seal').val(modalcontainerinfo_seal);

            // Change Lot
            var modalcontainerinfo_lot = button.data('modalcontainerinfo_lot')
            var modalcontainerinfo_lot_name = button.data('modalcontainerinfo_lotname')
            if(modalcontainerinfo_lot){
                $(ev.target).find('.container-contno').append('<option value=' + modalcontainerinfo_lot + ' selected=True>' + modalcontainerinfo_lot_name + '</option>');
            }
            
            // Change the Commodity
            var modalcontainerinfo_commodity = button.data('modalcontainerinfo_commodity')
            if (modalcontainerinfo_commodity){
                for (var i = 0; i < modalcontainerinfo_commodity.length; i++){
                    var css_name = '.container-commodity' + String(i+1) + '-' + String(modalcontainerinfo_commodity[i])
                    $(ev.target).find(css_name).attr("selected","selected");
                }
            }
            // Change the HS
            var modalcontainerinfo_hs = button.data('modalcontainerinfo_hs')
            var hs1 = $(ev.target).find('.container-hs1')
            var hs2 = $(ev.target).find('.container-hs2')
            var hs3 = $(ev.target).find('.container-hs3')
            var hs4 = $(ev.target).find('.container-hs4')
            var hs5 = $(ev.target).find('.container-hs5')
            if (modalcontainerinfo_hs){
                this._rpc({
                    model: 'sale.order',
                    method: 'get_hs_code',
                    args: [modalcontainerinfo_hs]
                }).then(function (result){
                    hs1.val(result[0])
                    hs2.val(result[1])
                    hs3.val(result[2])
                    hs4.val(result[3])
                    hs5.val(result[4])
                });
            }
        }
        $(ev.target).addClass('modal_shown');
    },
})
});
