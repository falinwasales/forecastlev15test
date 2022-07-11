odoo.define('operating_unit_selector.SwitchCompanyMenu', function(require) {
"use strict";

var SwitchCompanyMenu = require('web.SwitchCompanyMenu');
var session = require('web.session');

SwitchCompanyMenu.include({
    /**
     * @override
     *
     * @param {object} state - At Start add mapping
     * mapping is a list of company and operating unit relation (similar to many2many table)
     * structure [(company ID , operating unit ID)]
     * example [(1,1),(2,2)]
     */
    willStart: function (state) {
        var self = this;
        this.company_operating_unit_mapping = session.company_operating_unit_map;
        return this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {MouseEvent|KeyEvent} ev
     * We manage Company Click Behavior
     * With Opearating Unit switcher, swithcing company doesn't make sense anymore
     * With assumpstion that 1 Company always have minimum 1 Operating Unit
     */
    _onSwitchCompanyClick: function (ev) {
        if (ev.type == 'keydown' && ev.which != $.ui.keyCode.ENTER && ev.which != $.ui.keyCode.SPACE) {
            return;
        }
        ev.preventDefault();
        ev.stopPropagation();
        return;
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {MouseEvent|KeyEvent} ev
     * We manage Company Toggle Behavior
     * With Opearating Unit switcher, swithcing company doesn't make sense anymore
     * With assumpstion that 1 Company always have minimum 1 Operating Unit
     */
    _onToggleCompanyClick: function (ev) {
        if (ev.type == 'keydown' && ev.which != $.ui.keyCode.ENTER && ev.which != $.ui.keyCode.SPACE) {
            return;
        }
        ev.preventDefault();
        ev.stopPropagation();
        return true
    },
});

});
