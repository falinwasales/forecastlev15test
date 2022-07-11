odoo.define('forecastle_hr.image_specify', function (require){
    'use strict';

    var core = require('web.core');
    var time = require('web.time');
    const {ReCaptcha} = require('google_recaptcha.ReCaptchaV3');
    var ajax = require('web.ajax');
    // var publicWidget = require('web.public.widget');
    const dom = require('web.dom');
    var website_form = require('website_form.s_website_form');
    var publicWidget = require('web.public.widget');

    var _t = core._t;


    publicWidget.registry.s_website_form.include({
        /**
         * @override
         */
        check_error_fields: function (error_fields) {
            var self = this;
            var form_valid = true;
            this.$target.find('.form-field, .s_website_form_field').each(function (k, field) { // !compatibility
                var $field = $(field);
                var field_name = $field.find('.col-form-label').attr('for');
                
                // Validate inputs for this field
                var inputs = $field.find('.s_website_form_input, .o_website_form_input').not('#editable_select'); // !compatibility
                var invalid_inputs = inputs.toArray().filter(function (input, k, inputs) {
                    // Special check for multiple required checkbox for same
                    // field as it seems checkValidity forces every required
                    // checkbox to be checked, instead of looking at other
                    // checkboxes with the same name and only requiring one
                    // of them to be checked.
                    if (input.required && input.type === 'checkbox') {
                        // Considering we are currently processing a single
                        // field, we can assume that all checkboxes in the
                        // inputs variable have the same name
                        var checkboxes = _.filter(inputs, function (input) {
                            return input.required && input.type === 'checkbox';
                        });
                        return !_.any(checkboxes, checkbox => checkbox.checked);
                        
                        // Special cases for dates and datetimes
                    } else if ($(input).hasClass('s_website_form_date') || $(input).hasClass('o_website_form_date')) { // !compatibility
                        if (!self.is_datetime_valid(input.value, 'date')) {
                            return true;
                        }
                    } else if ($(input).hasClass('s_website_form_datetime') || $(input).hasClass('o_website_form_datetime')) { // !compatibility
                        if (!self.is_datetime_valid(input.value, 'datetime')) {
                            return true;
                        }
                    }

                    if (input.type === 'file' && input.accept === 'image/png, image/gif, image/jpeg')
                    {
                        var image = $field.find('.s_website_form_input, .o_website_form_input, .image').not('#editable_select'); 
                        // var get_image = image.filter(img => img)
                        for (var i = 0; i < image.length; i++) {
                            var oImage = image[i];
                            if (oImage.type == "file"){
                                var oName = oImage.value;
                                var oFile = oName.split('.').pop();
                                if (oFile.length > 0) {
                                    if (oFile != 'jpeg' && oFile != 'png' && oFile != 'jpg'){
                                        alert("One of your file(Image) is not supported, please upload the correct typefile!");
                                        return true;
                                    }
                                }
                            }
                        }
                    }

                    if (input.type === 'file' && input.accept === 'application/pdf')
                    {
                        var pdf = $field.find('.s_website_form_input, .o_website_form_input, .pdf').not('#editable_select'); 
                        // var get_image = image.filter(img => img)
                        for (var i = 0; i < pdf.length; i++) {
                            var oPdf = pdf[i];
                            if (oPdf.type == "file"){
                                var pName = oPdf.value;
                                var oFile = pName.split('.').pop();
                                if (oFile.length > 0) {
                                    if (oFile != 'pdf'){
                                        alert("One of your file(PDF) is not supported, please upload the correct typefile!");
                                        return true;
                                    }
                                }
                            }
                        }
                    }

                    if (input.type === 'tel')
                    {
                        var phone = $field.find('.form-control, .s_website_form_input, .phone1').not('#editable_select');
                        var format = /[A-Za-z!@#$%^&*()_\-=\[\]{};':"\\|,.<>\/?]+/;

                        for(var i = 0; i < phone.length; i++){
                            var ophone = phone[i];
                            var ophone2 = ophone.value;
                            if (ophone2.length > 0) {
                                if(ophone2.toString().match(format))
                                {
                                    console.log('GOOD')
                                    alert("There must be no (-) symbol or alphabet in phone section");
                                    return true;
                                }
                            }
                        }
                    
                    }

                    return !input.checkValidity();
                });

                // Update field color if invalid or erroneous
                $field.removeClass('o_has_error').find('.form-control, .custom-select').removeClass('is-invalid');
                if (invalid_inputs.length || error_fields[field_name]) {
                    $field.addClass('o_has_error').find('.form-control, .custom-select').addClass('is-invalid');
                    if (_.isString(error_fields[field_name])) {
                        $field.popover({content: error_fields[field_name], trigger: 'hover', container: 'body', placement: 'top'});
                        // update error message and show it.
                        $field.data("bs.popover").config.content = error_fields[field_name];
                        $field.popover('show');
                    }
                    form_valid = false;
                }
            });
            console.log("XXXXXXXXXXXXXXXXXXX")
            return form_valid;
        },
    });    
});