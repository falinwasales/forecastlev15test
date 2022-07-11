odoo.define('printnode.download_menu', function (require) {
    "use strict";

    const Context = require('web.Context');
    const DropdownMenu = require("web.DropdownMenu");
    const DropdownMenuItem = require('web.DropdownMenuItem');

    class DownloadDDMenuItem extends DropdownMenuItem {
        constructor() {
            super(...arguments);
            this.downloadOnly = true;
        }
    }

    class DownloadDDMenu extends DropdownMenu {
    }

    DownloadDDMenu.template = 'printnode.DownloadDDMenu';
    DownloadDDMenu.components = { DownloadDDMenuItem };

    const ActionMenus = require("web.ActionMenus");
    const patchMixin = require("web.patchMixin");
    const PatchableActionMenus = patchMixin(ActionMenus);

    PatchableActionMenus.patch("printnode.ActionMenus", (T) => {
        class DownloadActionMenus extends T {
            async willStart() {
                await super.willStart(...arguments);
                this.printnode_enabled = this.env.session.printnode_enabled;
            }

            async _executeAction(action) {
                if (event.originalComponent.downloadOnly) {
                    // If selected from Download menu add additional option
                    let activeIds = this.props.activeIds;
                    if (this.props.isDomainSelected) {
                        activeIds = await this.rpc({
                            model: this.env.action.res_model,
                            method: 'search',
                            args: [this.props.domain],
                            kwargs: {
                                limit: this.env.session.active_ids_limit,
                            },
                        });
                    }
                    const activeIdsContext = {
                        active_id: activeIds[0],
                        active_ids: activeIds,
                        active_model: this.env.action.res_model,
                    };
                    if (this.props.domain) {
                        // keep active_domain in context for backward compatibility
                        // reasons, and to allow actions to bypass the active_ids_limit
                        activeIdsContext.active_domain = this.props.domain;
                    }

                    const context = new Context(this.props.context, activeIdsContext).eval();
                    const result = await this.rpc({
                        route: '/web/action/load',
                        params: { action_id: action.id, context },
                    });
                    result.context = new Context(result.context || {}, activeIdsContext)
                        .set_eval_context(context);
                    result.flags = result.flags || {};
                    result.flags.new_window = true;
                    this.trigger('do-action', {
                        action: result,
                        options: {
                            // here we add option
                            download: true,
                            on_close: () => this.trigger('reload'),
                        },
                    });
                } else {
                    return super._executeAction(...arguments);
                }
            }
        }
        return DownloadActionMenus;
    });

    ActionMenus.components.DownloadDDMenu = DownloadDDMenu;

    const ControlPanel = require("web.ControlPanel");
    ControlPanel.components.ActionMenus =  PatchableActionMenus;

    return {
        DownloadDDMenuItem: DownloadDDMenu,
        DownloadDDMenu: DownloadDDMenu,
        PatchableActionMenus: PatchableActionMenus
    }
});
