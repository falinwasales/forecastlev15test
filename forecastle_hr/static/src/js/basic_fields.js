odoo.define('forecastle_hr.ZoomImage', function (require) {
    'use strict';

    var basic_fields = require('web.basic_fields');
    var core = require('web.core');
    var registry = require('web.field_registry');

    basic_fields.FieldBinaryImage.include({
        // Override
        _renderReadonly: function () {
            this._super.apply(this, arguments);

            if(this.nodeOptions.zoom) {
                var unique = this.recordData.__last_update;
                // Change Here
                var url = this._getImageUrl(this.model, this.res_id, this.name, unique);
                // End here
                var $img;
                var imageField = _.find(Object.keys(this.recordData), function(o) {
                    return o.startsWith('image_');
                });

                if(this.nodeOptions.background)
                {
                    if('tag' in this.nodeOptions) {
                        this.tagName = this.nodeOptions.tag;
                    }

                    if('class' in this.attrs) {
                        this.$el.addClass(this.attrs.class);
                    }

                    const image_field = this.field.manual ? this.name:'image_128';

                    var urlThumb = this._getImageUrl(this.model, this.res_id, image_field, unique);

                    this.$el.empty();
                    $img = this.$el;
                    $img.css('backgroundImage', 'url(' + urlThumb + ')');
                } else {
                    $img = this.$('img');
                }
                var zoomDelay = 0;
                if (this.nodeOptions.zoom_delay) {
                    zoomDelay = this.nodeOptions.zoom_delay;
                }

                if(this.recordData[imageField]) {
                    $img.attr('data-zoom', 1);
                    $img.attr('data-zoom-image', url);

                    $img.zoomOdoo({
                        event: 'mouseenter',
                        timer: zoomDelay,
                        attach: '.o_content',
                        attachToTarget: true,
                        onShow: function () {
                            var zoomHeight = Math.ceil(this.$zoom.height());
                            var zoomWidth = Math.ceil(this.$zoom.width());
                            if( zoomHeight < 128 && zoomWidth < 128) {
                                this.hide();
                            }
                            core.bus.on('keydown', this, this.hide);
                            core.bus.on('click', this, this.hide);
                        },
                        beforeAttach: function () {
                            this.$flyout.css({ width: '512px', height: '512px' });
                        },
                        preventClicks: this.nodeOptions.preventClicks,
                    });
                }
            }
        },
    })
});