from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class SuratTugasWizard(models.TransientModel):
    _name="surat.tugas.wizard"
    _description = "Surat Tugas"

    fal_nama_pemberi_tugas_wizard = fields.Many2one('hr.employee',string='Nama')
    fal_alamat_pemberi_tugas_wizard = fields.Char(string='Alamat')
    fal_jabatan_pemberi_tugas_wizard = fields.Char(string='Jabatan')

    fal_nama_penerima_tugas_wizard = fields.Many2one('hr.employee',string='Nama')
    fal_alamat_penerima_tugas_wizard = fields.Char(string='Alamat')
    fal_jabatan_penerima_tugas_wizard = fields.Char(string='Jabatan')

    @api.onchange('fal_nama_pemberi_tugas_wizard')
    def _onchange_pemberi_tugas(self):
        if self.fal_nama_pemberi_tugas_wizard:
            self.fal_alamat_pemberi_tugas_wizard = self.fal_nama_pemberi_tugas_wizard.company_id.street
            self.fal_jabatan_pemberi_tugas_wizard = (self.fal_nama_pemberi_tugas_wizard.department_id.name or '') +" "+ (self.fal_nama_pemberi_tugas_wizard.level or '')

    @api.onchange('fal_nama_penerima_tugas_wizard')
    def _onchange_penerima_tugas(self):
        if self.fal_nama_penerima_tugas_wizard:
            self.fal_alamat_penerima_tugas_wizard = self.fal_nama_penerima_tugas_wizard.company_id.street
            self.fal_jabatan_penerima_tugas_wizard = (self.fal_nama_penerima_tugas_wizard.department_id.name or '') +" "+ (self.fal_nama_penerima_tugas_wizard.level or '')

    def print_surat_tugas(self):
        active_id = self._context.get('active_id')
        sale_order = self.env['sale.order'].search([('id', '=', active_id)])

        temp_container = []
        for rec in sale_order.import_container_info_ids:
            temp_container.append(rec.no_container)
        import_no_container =  ', '.join(map(str, temp_container))

        sale_order.write({
            'fal_nama_pemberi_tugas': self.fal_nama_pemberi_tugas_wizard,
            'fal_alamat_pemberi_tugas':self.fal_alamat_pemberi_tugas_wizard,
            'fal_jabatan_pemberi_tugas':self.fal_jabatan_pemberi_tugas_wizard,
            'fal_nama_penerima_tugas':self.fal_nama_penerima_tugas_wizard,
            'fal_alamat_penerima_tugas':self.fal_alamat_penerima_tugas_wizard,
            'fal_jabatan_penerima_tugas':self.fal_jabatan_penerima_tugas_wizard,
            'temp_no_container': import_no_container,
        })

        return self.env.ref('forecastle_module.action_surat_tugas_report').report_action(sale_order)
