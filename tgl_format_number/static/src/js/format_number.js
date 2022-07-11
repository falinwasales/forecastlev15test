odoo.define("tgl_format_number.FieldFloat", function (require) {
    "use strict";

    var basic_fields = require("web.basic_fields");
    var translation = require("web.translation");
    var core = require('web.core');

    basic_fields.InputField.include({
        init: function () {
            this._super.apply(this, arguments);
            this.thousands_sep = core._t.database.parameters.thousands_sep || ',';
            this.decimal_point = core._t.database.parameters.decimal_point || '.';
            this.re = new RegExp("[^" + this.decimal_point + "-\\d]", "g");
        }
    });


    basic_fields.FieldMonetary.include({
        _onInput: function () {
            this._super();
            var self = this;
            $(this.$input).val(function (index, value) {
                var origin_value = value.replace(self.re, "").replace(/\B(?=((\d{3})+(?!\d)))/g, self.thousands_sep);
                var new_value = origin_value.split(self.decimal_point);
                var re = new RegExp("\\" + self.thousands_sep, "g");
                if (new_value.length > 1) {
                    new_value = new_value[0] + self.decimal_point + new_value[1].replace(re, '');
                }

                return new_value;
            });
        }
    });

    basic_fields.FieldFloat.include({
        _onInput: function () {
            this._super();
            var self = this;
            if(this.formatType === "float_time"){
                return;
            }
            $(this.$input).val(function (index, value) {
                var origin_value = value.replace(self.re, "").replace(/\B(?=((\d{3})+(?!\d)))/g, self.thousands_sep);
                var new_value = origin_value.split(self.decimal_point);
                var re = new RegExp("\\" + self.thousands_sep, "g");
                if (new_value.length > 1) {
                    new_value = new_value[0] + self.decimal_point + new_value[1].replace(re, '');
                }

                return new_value;
            });
        }
    });
    
});
