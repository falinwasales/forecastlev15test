odoo.define('printnode.status_menu', function (require) {
    "use strict";

    var core = require('web.core');
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    var _t = core._t;

    var ActionMenu = Widget.extend({
        template: 'printnode_status_menu',
        events: {
            'show.bs.dropdown': '_onPrintNodeStatusShow',
        },
        _onPrintNodeStatusShow: function (e) {
            this._rpc({
                model: 'printnode.account',
                method: 'get_limits',
            }).then((limits) => {
                if (limits.length) {
                    $('.o_printnode_status_menu_dropdown').html(
                        limits
                            .map(this._generateLimitMessage)
                            .join('<br>')
                    );
                } else {
                    $('.o_printnode_status_menu_dropdown').html(_t('No PrintNode accounts added'));
                }
                
            });
        },

        _generateLimitMessage: function(limit) {
            if (limit.error) {
                return _.str.sprintf(
                    '<b>%s</b>: %s',
                    limit.account,
                    _t("Something went wrong. Check the details on the PrintNode/Accounts page")
                );
            }
            return _.str.sprintf(_t('<b>%s</b>: %s/%s printed'), limit.account, limit.printed, limit.limits);
        }
    });

    SystrayMenu.Items.push(ActionMenu);

    return ActionMenu;
});
