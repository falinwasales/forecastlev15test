odoo.define('test_modulo.BasicView', function (require) {
"use strict";

var session = require('web.session');
var BasicView = require('web.BasicView');
BasicView.include({
        init: function(viewInfo, params) {
            var self = this;
            this._super.apply(this, arguments);
            var model = self.controllerParams.modelName in ['fce.port.code','fce.hs.code', 'fce.vessel', 'fce.group.code', 'fce.kpbc.code', 'fce.package.code', 'fce.voyage', 'commission.export'] ? 'True' : 'False';
            if(model) {
                session.user_has_group('forecastle_hide_archive.group_archive').then(function(has_group) {
                    if(!has_group) {
                        self.controllerParams.archiveEnabled = 'False' in viewInfo.fields;
                    }
                });
            }
        },
    });
});