odoo.define("configurable_chatter_position", function (require) {
    "use strict";

    /* eslint-disable no-unused-vars */

    var config = require("web.config");
    var FormController = require("web.FormController");
    var FormRenderer = require("web.FormRenderer");
    var session = require("web.session");

    FormController.include({
        renderButtons: function ($node) {
            var self = this;
            self._super.apply(self, arguments);
            if (self.$buttons) {
                self.$buttons.on(
                    "click",
                    ".o_chatter_position_bottom_right",
                    self._onConfgChatterPosition.bind(self)
                );
            }
        },
        _onConfgChatterPosition: function () {
            var self = this;
            if (self.renderer.currentChatterPosition === "bottom") {
                self.renderer.currentChatterPosition = "right";
            } else {
                self.renderer.currentChatterPosition = "bottom";
            }
            self.renderer.claimChatterPosition();
            self._rpc({
                route: "/configurable_chatter_position",
                params: {
                    chatter_position: self.renderer.currentChatterPosition,
                },
            });
        },
    });

    FormRenderer.include({
        init: function (parent, model, renderer, params) {
            var self = this;
            self._super.apply(self, arguments);
            if (session.user_context.chatter_position === "chatter_right") {
                self.currentChatterPosition = "right";
            } else {
                self.currentChatterPosition = "bottom";
            }
        },
        claimChatterPosition: function () {
            var self = this;
            var $form = $(".o_form_view");
            self.isMobile = config.device.isMobile;
            if (self.isMobile) {
                return;
            }
            if ($form.length === 1) {
                var $sheet = $form.find("div.o_form_sheet_bg");
                var $chatterarea = $form.find("div.o_FormRenderer_chatterContainer");
                if ($sheet.length === 1 && $chatterarea.length === 1) {
                    if (self.currentChatterPosition === "right") {
                        $form.css("display", "flex");
                        $sheet.css("width", "");
                        $sheet.find(".o_form_sheet").css("max-width", "");
                        $chatterarea.css("width", "");
                    } else {
                        $form.css("display", "block");
                        $sheet.css("width", "100%");
                        $sheet.find(".o_form_sheet").css("max-width", "100%");
                        $chatterarea.css("width", "100%");
                    }
                }
            }
        },
        _updateView: function ($newContent) {
            var self = this;
            self._super.apply(self, arguments);
            self.claimChatterPosition();
            setTimeout(function () {
                self.claimChatterPosition();
            }, 200);
            setTimeout(function () {
                self.claimChatterPosition();
            }, 600);
            setTimeout(function () {
                self.claimChatterPosition();
            }, 2000);
        },
    });
});
