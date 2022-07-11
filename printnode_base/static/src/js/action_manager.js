odoo.define('printnode_base.ReportActionManager', function(require) {
    "use strict";

    var ActionManager = require('web.ActionManager');
    var core = require('web.core');
    var framework = require('web.framework');
    var session = require('web.session');

    var _t = core._t;


    ActionManager.include({

        /**
         * Downloads a PDF report for the given url. It blocks the UI during the
         * report generation and download.
         *
         * @param {string} url
         * @returns {Promise} resolved when the report has been downloaded ;
         *   rejected if something went wrong during the report generation
         */
        _downloadReport: function(url, download_only) {
            var self = this;
            framework.blockUI();
            return new Promise(function(resolve, reject) {
                var type = 'qweb-' + url.split('/')[2];
                var blocked = !session.get_file({
                    url: '/report/download',
                    data: {
                        data: JSON.stringify([url, type, download_only]),
                        context: JSON.stringify(session.user_context),
                    },
                    success: resolve,
                    error: (error) => {
                        if (error.data.name == '418') {
                            if (error.message) {
                                self.do_notify(_t('Wow, the report is printed!'), _t('Well, actually it has been just sent to the printer via PrintNode service'), false);
                            }
                            resolve();
                        } else {
                            self.call('crash_manager', 'rpc_error', error);
                            reject();
                        }
                    },
                    complete: framework.unblockUI,
                });
                if (blocked) {
                    // AAB: this check should be done in get_file service directly,
                    // should not be the concern of the caller (and that way, get_file
                    // could return a promise)
                    var message = _t('A popup window with your report was blocked. You ' +
                        'may need to change your browser settings to allow ' +
                        'popup windows for this page.');
                    self.do_warn(_t('Warning'), message, true);
                }
            });
        },

        _triggerDownload: function (action, options, type){
            var self = this;
            var reportUrls = this._makeReportUrls(action);
            return this._downloadReport(reportUrls[type], options.download ? true : false).then(function () {
                if (action.close_on_report_download) {
                    var closeAction = { type: 'ir.actions.act_window_close' };
                    return self.doAction(closeAction, _.pick(options, 'on_close'));
                } else {
                    return options.on_close();
                }
            });
        },

    });
});
