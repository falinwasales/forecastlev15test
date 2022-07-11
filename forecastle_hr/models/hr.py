# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from datetime import datetime
from dateutil import relativedelta


class FceAcademicTranscript(models.Model):
    _name = 'fce.academic.transcript'

    name = fields.Char(string='Name')
    academic_transcript = fields.Binary('Academic Transcript')
    employee_id = fields.Many2one('hr.employee', string="Employee")
    applicant_id = fields.Many2one('hr.applicant', string="Applicant")


class FceFormalCertificate(models.Model):
    _name = 'fce.formal.certificate'

    name = fields.Char(string='Name')
    formal_certificate = fields.Binary('Formal Certificate')
    employee_id = fields.Many2one('hr.employee', string="Employee")
    applicant_id = fields.Many2one('hr.applicant', string="Applicant")


class FceInformalCertificate(models.Model):
    _name = 'fce.informal.certificate'

    name = fields.Char(string='Name')
    informal_certificate = fields.Binary('Informal Certificate')
    employee_id = fields.Many2one('hr.employee', string="Employee")
    applicant_id = fields.Many2one('hr.applicant', string="Applicant")


class HrEthnicity(models.Model):
    _name = 'fce.hr.ethnicity'

    name = fields.Char(string="Ethnicity")


class HrBukuDosa(models.Model):
    _name = 'fce.hr.buku.dosa'

    name = fields.Char(string='Issued By')
    level = fields.Selection([('ringan', 'Ringan'),('sedang', 'Sedang'),('berat', 'Berat')], string="Level", required=True)
    date = fields.Date(string='Tanggal', required=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=False, invisible=True)
    description = fields.Text(string="Deskripsi", required=True)
    attachment = fields.Binary(string="Attachment", required=True)


class HrEducation(models.Model):
    _name = 'fce.hr.education'

    name = fields.Char(string="Institution", required=1)
    jenjang_study = fields.Selection([
        ('sma', 'High School'),
        ('d3', 'D3 - Associate'),
        ('s1', 'S1 - Bachelor'),
        ('s2', 'S2 - Magister'),
        ('s3', 'S3 - Doctoral'),
        ('other', 'Others')
    ], string="Academic Degree")
    degree = fields.Char(string="courses")
    jurusan = fields.Char(string="Level")
    tahun_lulus = fields.Date(string="Graduate")
    ipk = fields.Float(string="GPA")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    formal_employee_id = fields.Many2one('hr.employee', string="Employee")
    formal_applicant_id = fields.Many2one('hr.applicant', string="Applicant")
    applicant_id = fields.Many2one('hr.applicant', string="Applicant")


class HrWorkExp(models.Model):
    _name = 'fce.hr.work.exp'

    name = fields.Char(string="Company Name")
    posisi = fields.Char(string="Position")
    jenis_pekerjaan = fields.Selection([
        ('purnawaktu', 'Full-Time'),
        ('paruhwaktu', 'Part-Time'),
        ('wiraswasta', 'Entrepreneur'),
        ('pekerjalepas', 'Freelance'),
        ('kontrak', 'Contract'),
        ('magang', 'Internship'),
        ('seasonal', 'Seasonal'),
    ], string="Employee Status")

    def _get_country(self):
        country = self.env.ref('base.id')
        return [('country_id', '=', country.id)]

    location_id = fields.Many2one('res.country.state', string="Location", domain=_get_country)
    tgl_mulai = fields.Date(string="Start Date")
    tgl_berakhir = fields.Date(string="End Date")
    deskripsi = fields.Char(string="Description")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    applicant_id = fields.Many2one('hr.applicant', string="Applicant")
    salary_history = fields.Float(string="History Salary")
    reference_letter = fields.Binary('Reference Letter')


class HrWorkAddress(models.Model):
    _name = 'fce.hr.work.address'

    name = fields.Char(string="Address")


class HrPrivInfo(models.Model):
    _name = 'fce.hr.priv.info'

    name = fields.Text(string="Address")
    address_type = fields.Selection([
        ('idcardaddress', 'ID Card Address'),
        ('currentaddress', 'Current Address'),
    ], string="Address Type")
    employee_id = fields.Many2one('hr.employee', string="Employee")


class HrEmergencyContact(models.Model):
    _name = 'fce.hr.emergency.contact'

    name = fields.Char(string="Name")
    phone = fields.Char(string="Phone")
    status = fields.Char(string="Status")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    applicant_id = fields.Many2one('hr.applicant', string="Applicant")
    relationship = fields.Char(string='Relationship')


class HrEmployeeBase(models.AbstractModel):
    _inherit = 'hr.employee.base'

    # Private Information
    personal_email = fields.Char('Personal Email')
    blood_type = fields.Selection([
        ('a', 'A'),
        ('ab', 'AB'),
        ('b', 'B'),
        ('o', 'O'),
    ], string="Blood Type")
    religion = fields.Selection([
        ('muslim', 'Islam'),
        ('kristen', 'Christian'),
        ('katolik', 'Catholic'),
        ('hindu', 'Hindu'),
        ('budha', 'Buddhist'),
        ('others', 'Others'),
    ], string="Religion")
    other_religion = fields.Char('Other Religion')
    ethnicity_id = fields.Many2one('fce.hr.ethnicity', string="Ethnicity")
    passport_expire_date = fields.Date(string="Passport Expire Date")
    formal_education_ids = fields.One2many('fce.hr.education', 'formal_employee_id', string="Formal Education")
    informal_education_ids = fields.One2many('fce.hr.education', 'employee_id', string="Informal Education")
    working_experience_ids = fields.One2many('fce.hr.work.exp', 'employee_id', string="Working Experience")
    address_ids = fields.One2many('fce.hr.priv.info', 'employee_id', string="Address")
    emergency_contact_ids = fields.One2many('fce.hr.emergency.contact', 'employee_id', string="Emergency Contact")
    formal_certificate_ids = fields.One2many('fce.formal.certificate', 'employee_id', string="Formal Certificate")
    informal_certificate_ids = fields.One2many('fce.informal.certificate', 'employee_id', string="Informal Certificate")
    academic_transcript_ids = fields.One2many('fce.academic.transcript', 'employee_id', string="Academic Transcript")

    # Work Information
    work_address_id = fields.Many2one('fce.hr.work.address', string="Work Address")

    def _get_country(self):
        country = self.env.ref('base.id')
        return [('country_id', '=', country.id)]

    work_location_id = fields.Many2one('res.country.state', string="Work Location", domain=_get_country)
    employment_status = fields.Selection([
        ('freelance', 'Freelance'),
        ('internship', 'Internship'),
        ('contract', 'Contract'),
        ('probation', 'Probation'),
        ('permanent', 'Permanent'),
    ], string="Employment Status")
    end_employment_date = fields.Date(string="End Employment Status Date")
    join_date = fields.Date(string="Join Date")
    duration_join_date = fields.Char('Duration', compute="_get_duration")
    level = fields.Selection([
        ('assistant', 'Assistant'),
        ('officer', 'Officer'),
        ('executive', 'Executive'),
        ('seniorexecutive', 'Senior Executive'),
        ('supervisor', 'Supervisor'),
        ('assistantmanager', 'Assistant Manager'),
        ('manager', 'Manager'),
        ('seniormanager', 'Senior Manager'),
        ('generalmanager', 'General Manager'),
        ('director', 'Director'),
        ('presidentdirector', 'President Director'),
        ('advisor', 'Advisor'),
    ], string="Level")
    functional_reports = fields.Many2many('hr.employee', 'employee_functional_rel', 'functional_id', 'employee_id', string="Functional Reports")

    phone = fields.Char(related='', string="Mobile Number")

    # HR Setting
    fal_i_agree = fields.Boolean(string='I Agree')
    term_and_condition = fields.Binary(string="Term And Condition", related="company_id.term_and_condition")

    def _get_duration(self):
        for emp in self:
            if emp.join_date:
                date1 = emp.join_date
                date2 = fields.Date.today()

                diff = relativedelta.relativedelta(date2, date1)

                years = diff.years
                months = diff.months
                days = diff.days
                emp.duration_join_date = "%s Years, %s Month, %s Days" % (years, months, days)
            else:
                emp.duration_join_date = False


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    ktp = fields.Binary('ID Card')
    kartu_keluarga = fields.Binary('Family Card')
    cv = fields.Binary('CV')
    kartu_bpjstk = fields.Binary('BPJSTK Card')
    kartu_bpjskes = fields.Binary('BPJSKES Card')
    pas_foto = fields.Binary('Pass Photo')
    sertifikat_training = fields.Binary('Formal Certificate')
    ijazah_training = fields.Binary('Informal Certificate')
    transkip_nilai = fields.Binary('Academic Transcript')
    npwp = fields.Binary('Tax ID')
    copy_cover_buku_tabungan = fields.Binary('Bank Account Cover')
    offering_later = fields.Binary('Offering Letter')
    confirmation_later = fields.Binary('Confirmation Letter')
    current_address = fields.Text(string="Current Address")
    id_card_address = fields.Text(string="ID Card Address")
    fal_employee_member_ids = fields.Many2many('hr.employee', 'all_employee_member_rel', 'member_id', 'employee_id', compute='_get_all_employee_member')
    phone = fields.Char(related='')
    home_number = fields.Char(string="Home Number")

    # Predictive Index
    predictive_index = fields.Binary('Predictive Index Results or DISC 1')
    filename_predictive_index = fields.Char('Title')
    predictive_index2 = fields.Binary('Predictive Index Results or DISC 2')
    filename_predictive_index2 = fields.Char('Title')
    predictive_index3 = fields.Binary('Predictive Index Results or DISC 3')
    filename_predictive_index3 = fields.Char('Title')
    predictive_index4 = fields.Binary('Predictive Index Results or DISC 4')
    filename_predictive_index4 = fields.Char('Title')

    # Formal Certificate
    formal_certificate1 = fields.Binary('Formal Certificate 1')
    filename_formal_certificate1 = fields.Char('Title')
    formal_certificate2 = fields.Binary('Formal Certificate 2')
    filename_formal_certificate2 = fields.Char('Title')
    formal_certificate3 = fields.Binary('Formal Certificate 3')
    filename_formal_certificate3 = fields.Char('Title')

    # Informal Certificate
    informal_certificate1 = fields.Binary('Informal Certificate 1')
    filename_informal_certificate1 = fields.Char('Title')
    informal_certificate2 = fields.Binary('Informal Certificate 2')
    filename_informal_certificate2 = fields.Char('Title')
    informal_certificate3 = fields.Binary('Informal Certificate 3')
    filename_informal_certificate3 = fields.Char('Title')
    informal_certificate4 = fields.Binary('Informal Certificate 4')
    filename_informal_certificate4 = fields.Char('Title')
    informal_certificate5 = fields.Binary('Informal Certificate 5')
    filename_informal_certificate5 = fields.Char('Title')

    # Academic Transcript
    academic_transcript1 = fields.Binary('Academic Transcript 1')
    filename_academic_transcript1 = fields.Char('Title')
    academic_transcript2 = fields.Binary('Academic Transcript 2')
    filename_academic_transcript2 = fields.Char('Title')
    academic_transcript3 = fields.Binary('Academic Transcript 3')
    filename_academic_transcript3 = fields.Char('Title')


    #Buku Dosa
    buku_dosa_line_ids = fields.One2many('fce.hr.buku.dosa','employee_id',string="Buku Dosa Lines")

    # home address
    address_home_id = fields.Many2one(
        'res.partner', 'Address', help='Enter here the private address of the employee, not the one linked to your company.',
        groups="hr.group_hr_user", tracking=True,
        domain="['&', ('customer_rank', '=', 0), ('supplier_rank', '=', 0)]")

    #HR Setting
    fal_i_agree = fields.Boolean(string='I Agree')

    def action_agree(self):
        for emp in self:
            emp.sudo().write({'fal_i_agree': True})

    def _get_all_employee_member(self):
        for user in self:
            team_obj = self.env['hr.employee']
            employees = []
            members = team_obj.search([('parent_id', '=', user.id)])
            if members:
                employee_members = members
                while employee_members:
                    for team in employee_members:
                        if team.id not in employees:
                            employees.append(team.id)
                        for member in team.child_ids:
                            if member.id not in employees:
                                employees.append(member.id)
                    employee_members = team_obj.search([('parent_id', 'in', employee_members.ids)])

                    if not employee_members:
                        employee_members = False
            user.fal_employee_member_ids = [(6, 0, employees)]


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    ktp = fields.Binary('ID Card', compute='_compute_image', compute_sudo=True)
    kartu_keluarga = fields.Binary('Family Card', compute='_compute_image', compute_sudo=True)
    cv = fields.Binary('CV', compute='_compute_image', compute_sudo=True)
    kartu_bpjstk = fields.Binary('BPJSTK Card', compute='_compute_image', compute_sudo=True)
    kartu_bpjskes = fields.Binary('BPJSKES Card', compute='_compute_image', compute_sudo=True)
    pas_foto = fields.Binary('Pass Photo', compute='_compute_image', compute_sudo=True)
    sertifikat_training = fields.Binary('Training Certificate', compute='_compute_image', compute_sudo=True)
    ijazah_training = fields.Binary('Training Document', compute='_compute_image', compute_sudo=True)
    transkip_nilai = fields.Binary('Academic Transcript', compute='_compute_image', compute_sudo=True)
    npwp = fields.Binary('Tax ID', compute='_compute_image', compute_sudo=True)
    copy_cover_buku_tabungan = fields.Binary('Copy of Saving Book Cover', compute='_compute_image', compute_sudo=True)
    offering_later = fields.Binary('Offering Letter', compute='_compute_image', compute_sudo=True)
    confirmation_later = fields.Binary('Confirmation Letter', compute='_compute_image', compute_sudo=True)
    phone = fields.Char(related='', string="Mobile Number")
    home_number = fields.Char(string="Home Number")
    term_and_condition = fields.Binary(string="Term And Condition", compute='_compute_image', compute_sudo=True)

    # Predictive Index
    predictive_index = fields.Binary('Predictive Index Results or DISC 1', compute='_compute_image', compute_sudo=True)
    filename_predictive_index = fields.Char('Title')
    predictive_index2 = fields.Binary('Predictive Index Results or DISC 2', compute='_compute_image', compute_sudo=True)
    filename_predictive_index2 = fields.Char('Title')
    predictive_index3 = fields.Binary('Predictive Index Results or DISC 3', compute='_compute_image', compute_sudo=True)
    filename_predictive_index3 = fields.Char('Title')
    predictive_index4 = fields.Binary('Predictive Index Results or DISC 4', compute='_compute_image', compute_sudo=True)
    filename_predictive_index4 = fields.Char('Title')
    # Formal Certificate
    filename_formal_certificate1 = fields.Char('Filename')
    filename_formal_certificate2 = fields.Char('Filename')
    filename_formal_certificate3 = fields.Char('Filename')

    # Informal Certificate
    filename_informal_certificate1 = fields.Char('Filename')
    filename_informal_certificate2 = fields.Char('Filename')
    filename_informal_certificate3 = fields.Char('Filename')
    filename_informal_certificate4 = fields.Char('Filename')
    filename_informal_certificate5 = fields.Char('Filename')

    # Academic Transcript
    filename_academic_transcript1 = fields.Char('Filename')
    filename_academic_transcript2 = fields.Char('Filename')
    filename_academic_transcript3 = fields.Char('Filename')

    def _compute_image(self):
        super(HrEmployeePublic, self)._compute_image()
        for employee in self:
            # We have to be in sudo to have access to the images
            employee_id = self.sudo().env['hr.employee'].browse(employee.id)
            employee.ktp = employee_id.ktp
            employee.kartu_keluarga = employee_id.kartu_keluarga
            employee.cv = employee_id.cv
            employee.kartu_bpjstk = employee_id.kartu_bpjstk
            employee.kartu_bpjskes = employee_id.kartu_bpjskes
            employee.predictive_index = employee_id.predictive_index
            employee.predictive_index2 = employee_id.predictive_index2
            employee.predictive_index3 = employee_id.predictive_index3
            employee.predictive_index4 = employee_id.predictive_index4
            employee.pas_foto = employee_id.pas_foto
            employee.sertifikat_training = employee_id.sertifikat_training
            employee.ijazah_training = employee_id.ijazah_training
            employee.transkip_nilai = employee_id.transkip_nilai
            employee.npwp = employee_id.npwp
            employee.copy_cover_buku_tabungan = employee_id.copy_cover_buku_tabungan
            employee.offering_later = employee_id.offering_later
            employee.confirmation_later = employee_id.confirmation_later
            employee.formal_certificate1 = employee_id.formal_certificate1
            employee.formal_certificate2 = employee_id.formal_certificate2
            employee.formal_certificate3 = employee_id.formal_certificate3
            employee.informal_certificate1 = employee_id.informal_certificate1
            employee.informal_certificate2 = employee_id.informal_certificate2
            employee.informal_certificate3 = employee_id.informal_certificate3
            employee.informal_certificate4 = employee_id.informal_certificate4
            employee.informal_certificate5 = employee_id.informal_certificate5
            employee.academic_transcript1 = employee_id.academic_transcript1
            employee.academic_transcript2 = employee_id.academic_transcript2
            employee.academic_transcript3 = employee_id.academic_transcript3
            employee.term_and_condition = employee_id.term_and_condition


class User(models.Model):
    _inherit = ['res.users']

    personal_email = fields.Char(related="employee_id.personal_email", readonly=False, related_sudo=False)
    home_number = fields.Char(related="employee_id.home_number", readonly=False, related_sudo=False)
    blood_type = fields.Selection(related="employee_id.blood_type", readonly=False, related_sudo=False)
    religion = fields.Selection(related="employee_id.religion", readonly=False, related_sudo=False)
    other_religion = fields.Char(related="employee_id.other_religion", readonly=False, related_sudo=False)
    ethnicity_id = fields.Many2one(related="employee_id.ethnicity_id", readonly=False, related_sudo=False)
    passport_expire_date = fields.Date(related="employee_id.passport_expire_date", readonly=False, related_sudo=False)
    formal_education_ids = fields.One2many(related="employee_id.formal_education_ids", readonly=False, related_sudo=False)
    informal_education_ids = fields.One2many(related="employee_id.informal_education_ids")
    working_experience_ids = fields.One2many(related="employee_id.working_experience_ids", readonly=False, related_sudo=False)
    address_ids = fields.One2many(related="employee_id.address_ids", readonly=False, related_sudo=False)
    emergency_contact_ids = fields.One2many(related="employee_id.emergency_contact_ids", readonly=False, related_sudo=False)
    formal_certificate_ids = fields.One2many(related="employee_id.formal_certificate_ids", readonly=False, related_sudo=False)
    informal_certificate_ids = fields.One2many(related="employee_id.informal_certificate_ids", readonly=False, related_sudo=False)
    academic_transcript_ids = fields.One2many(related="employee_id.academic_transcript_ids", readonly=False, related_sudo=False)

    # Work Information
    work_address_id = fields.Many2one(related="employee_id.work_address_id", readonly=False, related_sudo=False)
    work_location_id = fields.Many2one(related="employee_id.work_location_id", readonly=False, related_sudo=False)
    employment_status = fields.Selection(related="employee_id.employment_status", readonly=False, related_sudo=False)
    end_employment_date = fields.Date(related="employee_id.end_employment_date", readonly=False, related_sudo=False)
    join_date = fields.Date(related="employee_id.join_date")
    duration_join_date = fields.Char(related="employee_id.duration_join_date", readonly=False, related_sudo=False)
    level = fields.Selection(related="employee_id.level", readonly=False, related_sudo=False)
    functional_reports = fields.Many2many(related="employee_id.functional_reports", readonly=False, related_sudo=False)

    current_address = fields.Text(related="employee_id.current_address", readonly=False, related_sudo=False)
    id_card_address = fields.Text(related="employee_id.id_card_address", readonly=False, related_sudo=False)
    fal_employee_member_ids = fields.Many2many(related="employee_id.fal_employee_member_ids", readonly=False, related_sudo=False)
    ktp = fields.Binary(related="employee_id.ktp", readonly=False, related_sudo=False)
    kartu_keluarga = fields.Binary(related="employee_id.kartu_keluarga", readonly=False, related_sudo=False)
    cv = fields.Binary(related="employee_id.cv", readonly=False, related_sudo=False)
    kartu_bpjstk = fields.Binary(related="employee_id.kartu_bpjstk", readonly=False, related_sudo=False)
    kartu_bpjskes = fields.Binary(related="employee_id.kartu_bpjskes", readonly=False, related_sudo=False)
    predictive_index = fields.Binary(related="employee_id.predictive_index", readonly=False, related_sudo=False)
    filename_predictive_index = fields.Char(related="employee_id.filename_predictive_index", readonly=False, related_sudo=False)
    predictive_index2 = fields.Binary(related="employee_id.predictive_index2", readonly=False, related_sudo=False)
    filename_predictive_index2 = fields.Char(related="employee_id.filename_predictive_index2", readonly=False, related_sudo=False)
    predictive_index3 = fields.Binary(related="employee_id.predictive_index3", readonly=False, related_sudo=False)
    filename_predictive_index3 = fields.Char(related="employee_id.filename_predictive_index3", readonly=False, related_sudo=False)
    predictive_index4 = fields.Binary(related="employee_id.predictive_index4", readonly=False, related_sudo=False)
    filename_predictive_index4 = fields.Char(related="employee_id.filename_predictive_index4", readonly=False, related_sudo=False)
    pas_foto = fields.Binary(related="employee_id.pas_foto", readonly=False, related_sudo=False)
    sertifikat_training = fields.Binary(related="employee_id.sertifikat_training", readonly=False, related_sudo=False)
    ijazah_training = fields.Binary(related="employee_id.ijazah_training", readonly=False, related_sudo=False)
    transkip_nilai = fields.Binary(related="employee_id.transkip_nilai", readonly=False, related_sudo=False)
    npwp = fields.Binary(related="employee_id.npwp", readonly=False, related_sudo=False)
    copy_cover_buku_tabungan = fields.Binary(related="employee_id.copy_cover_buku_tabungan", readonly=False, related_sudo=False)
    offering_later = fields.Binary(related="employee_id.offering_later", readonly=False, related_sudo=False)
    confirmation_later = fields.Binary(related="employee_id.confirmation_later", readonly=False, related_sudo=False)

    # Formal Certificate
    formal_certificate1 = fields.Binary(related="employee_id.formal_certificate1", readonly=False, related_sudo=False)
    filename_formal_certificate1 = fields.Char(related="employee_id.filename_formal_certificate1", readonly=False, related_sudo=False)
    formal_certificate2 = fields.Binary(related="employee_id.formal_certificate2", readonly=False, related_sudo=False)
    filename_formal_certificate2 = fields.Char(related="employee_id.filename_formal_certificate2", readonly=False, related_sudo=False)
    formal_certificate3 = fields.Binary(related="employee_id.formal_certificate3", readonly=False, related_sudo=False)
    filename_formal_certificate3 = fields.Char(related="employee_id.filename_informal_certificate3", readonly=False, related_sudo=False)

    # Informal Certificate
    informal_certificate1 = fields.Binary(related="employee_id.informal_certificate1", readonly=False, related_sudo=False)
    filename_informal_certificate1 = fields.Char(related="employee_id.filename_informal_certificate1", readonly=False, related_sudo=False)
    informal_certificate2 = fields.Binary(related="employee_id.informal_certificate2", readonly=False, related_sudo=False)
    filename_informal_certificate2 = fields.Char(related="employee_id.filename_informal_certificate2", readonly=False, related_sudo=False)
    informal_certificate3 = fields.Binary(related="employee_id.informal_certificate3", readonly=False, related_sudo=False)
    filename_informal_certificate3 = fields.Char(related="employee_id.filename_informal_certificate3", readonly=False, related_sudo=False)
    informal_certificate4 = fields.Binary(related="employee_id.informal_certificate4", readonly=False, related_sudo=False)
    filename_informal_certificate4 = fields.Char(related="employee_id.filename_informal_certificate4", readonly=False, related_sudo=False)
    informal_certificate5 = fields.Binary(related="employee_id.informal_certificate5", readonly=False, related_sudo=False)
    filename_informal_certificate5 = fields.Char(related="employee_id.filename_informal_certificate5", readonly=False, related_sudo=False)

    # Academic Transcript
    academic_transcript1 = fields.Binary(related="employee_id.academic_transcript1", readonly=False, related_sudo=False)
    filename_academic_transcript1 = fields.Char(related="employee_id.filename_informal_certificate1", readonly=False, related_sudo=False)
    academic_transcript2 = fields.Binary(related="employee_id.academic_transcript2", readonly=False, related_sudo=False)
    filename_academic_transcript2 = fields.Char(related="employee_id.filename_informal_certificate2", readonly=False, related_sudo=False)
    academic_transcript3 = fields.Binary(related="employee_id.academic_transcript3", readonly=False, related_sudo=False)
    filename_academic_transcript3 = fields.Char(related="employee_id.filename_informal_certificate3", readonly=False, related_sudo=False)

    # Sign
    filename_personal_sign = fields.Binary("Electronic Signature")


class ResCompany(models.Model):
    _inherit = 'res.company'

    term_and_condition = fields.Binary(string="Term And Condition")
