odoo.define('bi_sql_editor.ListRenderer', function (require) {
"use_strict";
const ListRenderer = require('web.ListRenderer');
ListRenderer.include({
    /**
     * Handles the assignation of default widths for each column header.
     * If the list is empty, an arbitrary absolute or relative width will be
     * given to the header
     *
     * @see _getColumnWidth for detailed information about which width is
     * given to a certain field type.
     * TOKOPDA ADDONS, For SOME FIELDS WE WILL MANUALLY FIX THE COLUMN WIDTH
     *
     * @private
     */
    _computeDefaultWidths: function () {
        const isListEmpty = !this._hasVisibleRecords(this.state);
        const relativeWidths = [];
        this.columns.forEach(column => {
            const th = this._getColumnHeader(column);
            if (th.offsetParent === null) {
                relativeWidths.push(false);
            } else {
                const width = this._getColumnWidth(column);
                const ff = ['supplier_id', 'description_id', 'assembly_item_id', 'remark', 'article_no', 'size_ids', 'color_id', 'width', 'buyer_id', 'cons_percentage', 'cons_per_dz', 'uom_id', 'pricelist_id', 'cost_term_ids', 'original_price', 'additional_term', 'additional_cost', 'total_price', 'cost_per_dz', 'cost_percentage', 'additional_notes'];
                if (width.match(/[a-zA-Z]/)) { // absolute width with measure unit (e.g. 100px)
                    if (ff.includes(column.attrs.name)){
                        if (isListEmpty) {
                            th.style.width = width;
                        } else {
                            // If there are records, we force a min-width for fields with an absolute
                            // width to ensure a correct rendering in edition
                            th.style.minWidth = width;
                            th.style.width = width;
                        }
                        relativeWidths.push(false);
                    }else{
                        if (isListEmpty) {
                            th.style.width = width;
                        } else {
                            // If there are records, we force a min-width for fields with an absolute
                            // width to ensure a correct rendering in edition
                            th.style.minWidth = width;
                        }
                        relativeWidths.push(false);
                    }
                } else { // relative width expressed as a weight (e.g. 1.5)
                    relativeWidths.push(parseFloat(width, 10));
                }
            }
        });

        // Assignation of relative widths
        if (isListEmpty) {
            const totalWidth = this._getColumnsTotalWidth(relativeWidths);
            for (let i in this.columns) {
                if (relativeWidths[i]) {
                    const th = this._getColumnHeader(this.columns[i]);
                    th.style.width = (relativeWidths[i] / totalWidth * 100) + '%';
                }
            }
            // Manualy assigns trash icon header width since it's not in the columns
            const trashHeader = this.el.getElementsByClassName('o_list_record_remove_header')[0];
            if (trashHeader) {
                trashHeader.style.width = '32px';
            }
        }
    },
});

});
