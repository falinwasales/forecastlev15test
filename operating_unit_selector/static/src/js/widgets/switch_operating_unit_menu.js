odoo.define('operating_unit_selector.SwitchOperatingUnitMenu', function(require) {
"use strict";
/**
 * When Odoo is configured in multi-company mode, users should obviously be able
 * to switch their interface from one company to the other.  This is the purpose
 * of this widget, by displaying a dropdown menu in the systray.
 */

var config = require('web.config');
var core = require('web.core');
var session = require('web.session');
var SystrayMenu = require('web.SystrayMenu');
var SwitchCompanyMenu = require('web.SwitchCompanyMenu');
var Widget = require('web.Widget');

var _t = core._t;

var SwitchOperatingUnitMenu = Widget.extend({
    template: 'SwitchOperatingUnitMenu',
    events: {
        'click .dropdown-item[data-menu] div.log_into': '_onSwitchOperatingUnitClick',
        'click .dropdown-item[data-menu] div.toggle_company': '_onToggleOperatingUnitClick',
    },
    /**
     * @override
     */
    init: function () {
        this._super.apply(this, arguments);
        this.isMobile = config.device.isMobile;
        this._onSwitchOperatingUnitClick = _.debounce(this._onSwitchOperatingUnitClick, 1500, true);
    },

    /**
     * @override
     */
    willStart: function () {
        var self = this;
        // Company Parameter
        this.allowed_company_ids = String(session.user_context.allowed_company_ids)
                                    .split(',')
                                    .map(function (id) {return parseInt(id);});
        this.user_companies = session.user_companies.allowed_companies;
        this.current_company = this.allowed_company_ids[0];
        this.current_company_name = _.find(session.user_companies.allowed_companies, function (company) {
            return company[0] === self.current_company;
        })[1];
        // Opearint Unit Parameter
        this.operating_unit_ids = session.user_operating_units.assigned_operating_units.map(function (id) {return parseInt(id);})
        this.user_operating_units = session.user_operating_units.operating_units;
        this.current_operating_unit = session.user_operating_units.current_operating_unit[0];
        this.current_operating_unit_name = session.user_operating_units.current_operating_unit[1];
        this.company_operating_unit_mapping = session.company_operating_unit_map;

        // Auto click operating unit if mapping not match
        // Very dirty ways, but whatever
        for (var i = 0; i<this.company_operating_unit_mapping.length; i++){
            // Operating Unit company are not match selected company
            // Automatically click setOperatingUnits
            // And also include the company in case it did not have
            if (this.company_operating_unit_mapping[i][1] === this.current_operating_unit){
                if (this.company_operating_unit_mapping[i][0] !== this.current_company){
                    var new_allowed_company_ids = this.allowed_company_ids
                    if (new_allowed_company_ids.indexOf(this.company_operating_unit_mapping[i][0]) === -1){
                        new_allowed_company_ids.push(this.company_operating_unit_mapping[i][0])
                    }
                    session.setOperatingUnits(this.company_operating_unit_mapping[i][0], new_allowed_company_ids, this.current_operating_unit, this.operating_unit_ids);
                }
            }
        }
        return this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {MouseEvent|KeyEvent} ev
     * We manage Operating Unit Click Behavior
     * If we switch Operating Unit, means we need to switch the company too.
     * Also, when switching Operating Unit
     * So, we need to manage the allowed companies to match selected Operating Unit
     */
    _onSwitchOperatingUnitClick: function (ev) {
        var self = this;
        if (ev.type == 'keydown' && ev.which != $.ui.keyCode.ENTER && ev.which != $.ui.keyCode.SPACE) {
            return;
        }
        ev.preventDefault();
        ev.stopPropagation();
        var dropdownItem = $(ev.currentTarget).parent();
        var dropdownMenu = dropdownItem.parent();
        var companyID = dropdownItem.data('company-id');
        var operating_unit_ids = this.operating_unit_ids;
        var company_operating_unit_mapping = this.company_operating_unit_mapping;
        if (dropdownItem.find('.fa-square-o').length) {
            // 1 enabled company: Stay in single company mode
            if (this.operating_unit_ids.length === 1) {
                dropdownMenu.find('.fa-check-square').removeClass('fa-check-square').addClass('fa-square-o');
                dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
                operating_unit_ids = [companyID]
            } else { // Multi company mode
                operating_unit_ids.push(companyID);
                dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
            }
        }
        $(ev.currentTarget).attr('aria-pressed', 'true');
        // We store current operating unit / operating units
        // In case of any failure, it goes back to standard value without error
        var current_company_ids = this.allowed_company_ids
        var current_company_id = current_company_ids[0];
        for (var i = 0; i<company_operating_unit_mapping.length; i++){
            // If operating unit is the id selected, current company are the company of selected
            // operating unit
            if (company_operating_unit_mapping[i][1] === companyID){
                current_company_id = company_operating_unit_mapping[i][0]
            }
            // If operating unit ids is allowed (which is logical), #TDE: Do we need 1st if?
            // If companies selected is not in allowed companies list, include it
            if (operating_unit_ids.indexOf(company_operating_unit_mapping[i][1]) !== -1){
                if (current_company_ids.indexOf(company_operating_unit_mapping[i][0]) === -1){
                    current_company_ids.push(company_operating_unit_mapping[i][0])
                }
            }
        }
        session.setOperatingUnits(current_company_id, current_company_ids, companyID, operating_unit_ids);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {MouseEvent|KeyEvent} ev
     * We manage Operating Unit toggle Behavior
     * If we toggle In operating unit, means we need to give allowed in the companies too.
     * If we toggle Out, doesn't means we do not want to see the companies, so do nothing
     */
    _onToggleOperatingUnitClick: function (ev) {
        var self = this;
        if (ev.type == 'keydown' && ev.which != $.ui.keyCode.ENTER && ev.which != $.ui.keyCode.SPACE) {
            return;
        }
        ev.preventDefault();
        ev.stopPropagation();
        var dropdownItem = $(ev.currentTarget).parent();
        var companyID = dropdownItem.data('company-id');
        var operating_unit_ids = self.operating_unit_ids;
        var current_operating_unit = self.current_operating_unit;
        var company_operating_unit_mapping = self.company_operating_unit_mapping;
        if (dropdownItem.find('.fa-square-o').length) {
            operating_unit_ids.push(companyID);
            dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
        } else {
            if (operating_unit_ids.length > 1 && current_operating_unit != companyID){
                operating_unit_ids.splice(operating_unit_ids.indexOf(companyID), 1);
                dropdownItem.find('.fa-check-square').addClass('fa-square-o').removeClass('fa-check-square');
            }
        }
        // We store current operating unit / operating units
        // In case of any failure, it goes back to standard value without error
        var current_company_ids = self.allowed_company_ids
        var current_company_id = current_company_ids[0];
        // We need to know which companies it goes from the operating units
        var current_company_ids_by_operating_unit = []
        for (var i = 0; i<company_operating_unit_mapping.length; i++){
            if (operating_unit_ids.indexOf(company_operating_unit_mapping[i][1]) !== -1){
                if (current_company_ids.indexOf(company_operating_unit_mapping[i][0]) === -1){
                    current_company_ids.push(company_operating_unit_mapping[i][0])
                }
                if (current_company_ids_by_operating_unit.indexOf(company_operating_unit_mapping[i][0]) === -1){
                    current_company_ids_by_operating_unit.push(company_operating_unit_mapping[i][0])
                }
            }
        }
        session.setOperatingUnits(current_company_id, current_company_ids_by_operating_unit, current_operating_unit, operating_unit_ids);
    },

});

if (session.display_switch_operating_unit_menu) {
    var index = SystrayMenu.Items.indexOf(SwitchCompanyMenu);
    if (index >= 0) {
        SystrayMenu.Items.splice(0, 0, SwitchOperatingUnitMenu);
    }
    else{
        SystrayMenu.Items.push(SwitchOperatingUnitMenu);
    }
}

return SwitchOperatingUnitMenu;

});
