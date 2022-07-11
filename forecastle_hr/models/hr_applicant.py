# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import base64
from odoo.modules.module import get_module_resource


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    salary_expected = fields.Float("Expected Salary", group_operator="avg", help="Salary Expected by Applicant", tracking=True)

    def _get_image(self):
        image_path = get_module_resource('hr', 'static/src/img', 'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    def _compute_image(self):
        for item in self:
            image = self._get_image()
            item.image_1920 = image

    # Private Contact
    sequence = fields.Integer(related="stage_id.sequence")
    current_address = fields.Text(string="Current Address")
    id_card_address = fields.Text(string="ID Card Address")
    personal_email = fields.Char('Personal Email')
    km_home_work = fields.Integer(string="Home-Work Distance", tracking=True)
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

    # Citizenship
    country_id = fields.Many2one(
        'res.country', 'Nationality (Country)', tracking=True)
    identification_id = fields.Char(string='Identification No', tracking=True)
    passport_id = fields.Char('Passport No', tracking=True)
    passport_expire_date = fields.Date(string="Passport Expire Date")
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], tracking=True)
    place_of_birth = fields.Char('Place of Birth', tracking=True)
    country_of_birth = fields.Many2one('res.country', string="Country of Birth", tracking=True)
    birthday = fields.Date('Date of Birth', tracking=True)

    # Marital
    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='Marital Status', default='single', tracking=True)
    spouse_complete_name = fields.Char(string="Spouse Complete Name", tracking=True)
    spouse_birthdate = fields.Date(string="Spouse Birthdate", tracking=True)

    # Dependant
    children = fields.Integer(string='Number of Children', tracking=True)

    # Emergency
    emergency_name1 = fields.Char(string="Emergency Name")
    emergency_phone1 = fields.Char(string="Emergency Phone")
    emergency_relationship1 = fields.Char(string='Emergency Relationship')
    emergency_name2 = fields.Char(string="Emergency Name")
    emergency_phone2 = fields.Char(string="Emergency Phone")
    emergency_relationship2 = fields.Char(string='Emergency Relationship')
    emergency_name3 = fields.Char(string="Emergency Name")
    emergency_phone3 = fields.Char(string="Emergency Phone")
    emergency_relationship3 = fields.Char(string='Emergency Relationship')
    emergency_contact_ids = fields.One2many('fce.hr.emergency.contact', 'applicant_id', string="Emergency Contact")

    # Work Permit
    permit_no = fields.Char('Work Permit No', groups="hr.group_hr_user", tracking=True)
    visa_no = fields.Char('Visa No', groups="hr.group_hr_user", tracking=True)
    visa_expire = fields.Date('Visa Expire Date', groups="hr.group_hr_user", tracking=True)

    # Education
    formal_school1 = fields.Char(string="Formal School")
    formal_jenjang_study1 = fields.Selection([
        ('sma', 'High School'),
        ('d3', 'D3 - Associate'),
        ('s1', 'S1 - Bachelor'),
        ('s2', 'S2 - Magister'),
        ('s3', 'S3 - Doctoral'),
        ('other', 'Others')
    ], string="Academic Degree")
    formal_jurusan1 = fields.Char(string="Major")
    formal_tahun_lulus1 = fields.Date(string="Graduate")
    formal_ipk1 = fields.Float(string="GPA")
    formal_school2 = fields.Char(string="Formal School")
    formal_jenjang_study2 = fields.Selection([
        ('sma', 'High School'),
        ('d3', 'D3 - Associate'),
        ('s1', 'S1 - Bachelor'),
        ('s2', 'S2 - Magister'),
        ('s3', 'S3 - Doctoral'),
        ('other', 'Others')
    ], string="Academic Degree")
    formal_jurusan2 = fields.Char(string="Major")
    formal_tahun_lulus2 = fields.Date(string="Graduate")
    formal_ipk2 = fields.Float(string="GPA")
    formal_school3 = fields.Char(string="Formal School")
    formal_jenjang_study3 = fields.Selection([
        ('sma', 'High School'),
        ('d3', 'D3 - Associate'),
        ('s1', 'S1 - Bachelor'),
        ('s2', 'S2 - Magister'),
        ('s3', 'S3 - Doctoral'),
        ('other', 'Others')
    ], string="Academic Degree")
    formal_jurusan3 = fields.Char(string="Major")
    formal_tahun_lulus3 = fields.Date(string="Graduate")
    formal_ipk3 = fields.Float(string="GPA")
    formal_education_ids = fields.One2many('fce.hr.education', 'formal_applicant_id', string="Formal Education")

    informal_school1 = fields.Char(string="Formal School")
    informal_degree1 = fields.Char(string="Level")
    informal_jurusan1 = fields.Char(string="Major")
    informal_tahun_lulus1 = fields.Date(string="Graduate")
    informal_school2 = fields.Char(string="Formal School")
    informal_degree2 = fields.Char(string="Level")
    informal_jurusan2 = fields.Char(string="Major")
    informal_tahun_lulus2 = fields.Date(string="Graduate")
    informal_school3 = fields.Char(string="Formal School")
    informal_degree3 = fields.Char(string="Level")
    informal_jurusan3 = fields.Char(string="Major")
    informal_tahun_lulus3 = fields.Date(string="Graduate")
    informal_school4 = fields.Char(string="Formal School")
    informal_degree4 = fields.Char(string="Level")
    informal_jurusan4 = fields.Char(string="Major")
    informal_tahun_lulus4 = fields.Date(string="Graduate")
    informal_school5 = fields.Char(string="Formal School")
    informal_degree5 = fields.Char(string="Level")
    informal_jurusan5 = fields.Char(string="Major")
    informal_tahun_lulus5 = fields.Date(string="Graduate")
    informal_education_ids = fields.One2many('fce.hr.education', 'applicant_id', string="Informal Education")

    # Experience
    def _get_country(self):
        country = self.env.ref('base.id')
        return [('country_id', '=', country.id)]

    experience_company_name1 = fields.Char(string="Company Name")
    experience_posisi1 = fields.Char(string="Position")
    experience_jenis_pekerjaan1 = fields.Selection([
        ('purnawaktu', 'Full-Time'),
        ('paruhwaktu', 'Part-Time'),
        ('wiraswasta', 'Entrepreneur'),
        ('pekerjalepas', 'Freelance'),
        ('kontrak', 'Contract'),
        ('magang', 'Internship'),
        ('seasonal', 'Seasonal'),
    ], string="Employee Status")
    experience_location_id1 = fields.Many2one('res.country.state', string="Location", domain=_get_country)
    experience_tgl_mulai1 = fields.Date(string="Start Date")
    experience_tgl_berakhir1 = fields.Date(string="End Date")
    experience_reference_letter1 = fields.Binary('Reference Letter')
    experience_deskripsi1 = fields.Char(string="Description")
    experience_company_name2 = fields.Char(string="Company Name")
    experience_posisi2 = fields.Char(string="Position")
    experience_jenis_pekerjaan2 = fields.Selection([
        ('purnawaktu', 'Full-Time'),
        ('paruhwaktu', 'Part-Time'),
        ('wiraswasta', 'Entrepreneur'),
        ('pekerjalepas', 'Freelance'),
        ('kontrak', 'Contract'),
        ('magang', 'Internship'),
        ('seasonal', 'Seasonal'),
    ], string="Employee Status")
    experience_location_id2 = fields.Many2one('res.country.state', string="Location", domain=_get_country)
    experience_tgl_mulai2 = fields.Date(string="Start Date")
    experience_tgl_berakhir2 = fields.Date(string="End Date")
    experience_reference_letter2 = fields.Binary('Reference Letter')
    experience_deskripsi2 = fields.Char(string="Description")
    experience_company_name3 = fields.Char(string="Company Name")
    experience_posisi3 = fields.Char(string="Position")
    experience_jenis_pekerjaan3 = fields.Selection([
        ('purnawaktu', 'Full-Time'),
        ('paruhwaktu', 'Part-Time'),
        ('wiraswasta', 'Entrepreneur'),
        ('pekerjalepas', 'Freelance'),
        ('kontrak', 'Contract'),
        ('magang', 'Internship'),
        ('seasonal', 'Seasonal'),
    ], string="Employee Status")
    experience_location_id3 = fields.Many2one('res.country.state', string="Location", domain=_get_country)
    experience_tgl_mulai3 = fields.Date(string="Start Date")
    experience_tgl_berakhir3 = fields.Date(string="End Date")
    experience_reference_letter3 = fields.Binary('Reference Letter')
    experience_deskripsi3 = fields.Char(string="Description")
    working_experience_ids = fields.One2many('fce.hr.work.exp', 'applicant_id', string="Working Experience")

    experience_salary_history1 = fields.Float(string="History Salary")
    experience_salary_history2 = fields.Float(string="History Salary")
    experience_salary_history3 = fields.Float(string="History Salary")

    # Personal Information
    # trigger zoom
    @api.model
    def _default_image(self):
        image_path = get_module_resource('hr', 'static/src/img', 'default_image.png')
        return base64.b64encode(open(image_path, 'rb').read())

    image_1920 = fields.Image(compute='_compute_image')
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
    formal_certificate_ids = fields.One2many('fce.formal.certificate', 'applicant_id', string="Formal Certificate")
    informal_certificate_ids = fields.One2many('fce.informal.certificate', 'applicant_id', string="Informal Certificate")
    academic_transcript_ids = fields.One2many('fce.academic.transcript', 'applicant_id', string="Academic Transcript")

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

    @api.model
    def create(self, vals):
        emergency_contact_ids = []
        formal_education_ids = []
        informal_education_ids = []
        working_experience_ids = []
        if vals.get('emergency_name1'):
            emergency_contact_ids.append((0, 0, {
                'name': vals.get('emergency_name1'),
                'phone': vals.get('emergency_phone1'),
                'relationship': vals.get('emergency_relationship1'),
            }))
        if vals.get('emergency_name2'):
            emergency_contact_ids.append((0, 0, {
                'name': vals.get('emergency_name2'),
                'phone': vals.get('emergency_phone2'),
                'relationship': vals.get('emergency_relationship2'),
            }))
        if vals.get('emergency_name3'):
            emergency_contact_ids.append((0, 0, {
                'name': vals.get('emergency_name3'),
                'phone': vals.get('emergency_phone3'),
                'relationship': vals.get('emergency_relationship3'),
            }))

        if vals.get('formal_school1'):
            formal_education_ids.append((0, 0, {
                'name': vals.get('formal_school1'),
                'jenjang_study': vals.get('formal_jenjang_study1'),
                'jurusan': vals.get('formal_jurusan1'),
                'tahun_lulus': vals.get('formal_tahun_lulus1'),
                'ipk': vals.get('formal_ipk1'),
            }))
        if vals.get('formal_school2'):
            formal_education_ids.append((0, 0, {
                'name': vals.get('formal_school2'),
                'jenjang_study': vals.get('formal_jenjang_study2'),
                'jurusan': vals.get('formal_jurusan2'),
                'tahun_lulus': vals.get('formal_tahun_lulus2'),
                'ipk': vals.get('formal_ipk2'),
            }))

        if vals.get('formal_school3'):
            formal_education_ids.append((0, 0, {
                'name': vals.get('formal_school3'),
                'jenjang_study': vals.get('formal_jenjang_study3'),
                'jurusan': vals.get('formal_jurusan3'),
                'tahun_lulus': vals.get('formal_tahun_lulus3'),
                'ipk': vals.get('formal_ipk3'),
            }))

        if vals.get('informal_school1'):
            informal_education_ids.append((0, 0, {
                'name': vals.get('informal_school1'),
                'degree': vals.get('informal_degree1'),
                'jurusan': vals.get('informal_jurusan1'),
                'tahun_lulus': vals.get('informal_tahun_lulus1'),
            }))

        if vals.get('informal_school2'):
            informal_education_ids.append((0, 0, {
                'name': vals.get('informal_school2'),
                'degree': vals.get('informal_degree2'),
                'jurusan': vals.get('informal_jurusan2'),
                'tahun_lulus': vals.get('informal_tahun_lulus2'),
            }))

        if vals.get('informal_school3'):
            informal_education_ids.append((0, 0, {
                'name': vals.get('informal_school3'),
                'degree': vals.get('informal_degree3'),
                'jurusan': vals.get('informal_jurusan3'),
                'tahun_lulus': vals.get('informal_tahun_lulus3'),
            }))

        if vals.get('informal_school4'):
            informal_education_ids.append((0, 0, {
                'name': vals.get('informal_school4'),
                'degree': vals.get('informal_degree4'),
                'jurusan': vals.get('informal_jurusan4'),
                'tahun_lulus': vals.get('informal_tahun_lulus4'),
            }))

        if vals.get('informal_school5'):
            informal_education_ids.append((0, 0, {
                'name': vals.get('informal_school5'),
                'degree': vals.get('informal_degree5'),
                'jurusan': vals.get('informal_jurusan5'),
                'tahun_lulus': vals.get('informal_tahun_lulus5'),
            }))

        if vals.get('experience_company_name1'):
            working_experience_ids.append((0, 0, {
                'name': vals.get('experience_company_name1'),
                'posisi': vals.get('experience_posisi1'),
                'jenis_pekerjaan': vals.get('experience_jenis_pekerjaan1'),
                'location_id': vals.get('experience_location_id1'),
                'tgl_mulai': vals.get('experience_tgl_mulai1'),
                'tgl_berakhir': vals.get('experience_tgl_berakhir1'),
                'salary_history': vals.get('experience_salary_history1'),
                'reference_letter': vals.get('experience_reference_letter1'),
                'deskripsi': vals.get('experience_deskripsi1'),
            }))

        if vals.get('experience_company_name2'):
            working_experience_ids.append((0, 0, {
                'name': vals.get('experience_company_name2'),
                'posisi': vals.get('experience_posisi2'),
                'jenis_pekerjaan': vals.get('experience_jenis_pekerjaan2'),
                'location_id': vals.get('experience_location_id2'),
                'tgl_mulai': vals.get('experience_tgl_mulai2'),
                'tgl_berakhir': vals.get('experience_tgl_berakhir2'),
                'salary_history': vals.get('experience_salary_history2'),
                'reference_letter': vals.get('experience_reference_letter2'),
                'deskripsi': vals.get('experience_deskripsi2'),
            }))

        if vals.get('experience_company_name3'):
            working_experience_ids.append((0, 0, {
                'name': vals.get('experience_company_name3'),
                'posisi': vals.get('experience_posisi3'),
                'jenis_pekerjaan': vals.get('experience_jenis_pekerjaan3'),
                'location_id': vals.get('experience_location_id3'),
                'tgl_mulai': vals.get('experience_tgl_mulai3'),
                'tgl_berakhir': vals.get('experience_tgl_berakhir3'),
                'salary_history': vals.get('experience_salary_history3'),
                'reference_letter': vals.get('experience_reference_letter3'),
                'deskripsi': vals.get('experience_deskripsi3'),
            }))

        if emergency_contact_ids:
            vals.update({'emergency_contact_ids': emergency_contact_ids})
        if formal_education_ids:
            vals.update({'formal_education_ids': formal_education_ids})
        if informal_education_ids:
            vals.update({'informal_education_ids': informal_education_ids})
        if working_experience_ids:
            vals.update({'working_experience_ids': working_experience_ids})
        return super(HrApplicant, self).create(vals)

    def create_employee_from_applicant(self):
        res = super(HrApplicant, self).create_employee_from_applicant()
        context = res.get('context')
        vals = {}
        for applicant in self:
            emergency_contact_ids = []
            for emergency in applicant.emergency_contact_ids:
                emergency_contact_ids.append((0, 0, {
                    'name': emergency.name,
                    'phone': emergency.phone,
                    'status': emergency.status,
                }))

            formal_education_ids = []
            for formal_education in applicant.formal_education_ids:
                formal_education_ids.append((0, 0, {
                    'name': formal_education.name,
                    'jenjang_study': formal_education.jenjang_study,
                    'jurusan': formal_education.jurusan,
                    'tahun_lulus': formal_education.tahun_lulus,
                    'ipk': formal_education.ipk,
                }))

            informal_education_ids = []
            for informal_education in applicant.informal_education_ids:
                informal_education_ids.append((0, 0, {
                    'name': informal_education.name,
                    'degree': informal_education.degree,
                    'jurusan': informal_education.jurusan,
                    'tahun_lulus': informal_education.tahun_lulus,
                }))

            working_experience_ids = []
            for working_experience in applicant.working_experience_ids:
                working_experience_ids.append((0, 0, {
                    'name': working_experience.name,
                    'posisi': working_experience.posisi,
                    'jenis_pekerjaan': working_experience.jenis_pekerjaan,
                    'location_id': working_experience.location_id.id,
                    'tgl_mulai': working_experience.tgl_mulai,
                    'tgl_berakhir': working_experience.tgl_berakhir,
                    'salary_history': working_experience.salary_history,
                    'reference_letter': working_experience.reference_letter,
                    'deskripsi': working_experience.deskripsi,
                }))

            vals.update({
                'default_current_address': applicant.current_address,
                'default_id_card_address': applicant.id_card_address,
                'default_personal_email': applicant.email_from,
                'default_phone': applicant.partner_mobile,
                'default_home_number': applicant.partner_phone,
                'default_blood_type': applicant.blood_type,
                'default_religion': applicant.religion,
                'default_ethnicity_id': applicant.ethnicity_id.id,
                'default_country_id': applicant.country_id.id,
                'default_identification_id': applicant.identification_id,
                'default_passport_id': applicant.passport_id,
                'default_passport_expire_date': applicant.passport_expire_date,
                'default_gender': applicant.gender,
                'default_birthday': applicant.birthday,
                'default_place_of_birth': applicant.place_of_birth,
                'default_country_of_birth': applicant.country_of_birth.id,
                'default_marital': applicant.marital,
                'default_ktp': applicant.ktp,
                'default_kartu_keluarga': applicant.kartu_keluarga,
                'default_pas_foto': applicant.pas_foto,
                'default_kartu_bpjstk': applicant.kartu_bpjstk,
                'default_kartu_bpjskes': applicant.kartu_bpjskes,
                'default_npwp': applicant.npwp,
                'default_cv': applicant.cv,
                'default_emergency_contact_ids': emergency_contact_ids,
                'default_formal_education_ids': formal_education_ids,
                'default_informal_education_ids': informal_education_ids,
                'default_working_experience_ids': working_experience_ids,
                'default_predictive_index': applicant.predictive_index,
                'default_filename_predictive_index': applicant.filename_predictive_index,
                'default_predictive_index2': applicant.predictive_index2,
                'default_filename_predictive_index2': applicant.filename_predictive_index2,
                'default_predictive_index3': applicant.predictive_index3,
                'default_filename_predictive_index3': applicant.filename_predictive_index3,
                'default_predictive_index4': applicant.predictive_index4,
                'default_filename_predictive_index4': applicant.filename_predictive_index4,
                'default_formal_certificate1': applicant.formal_certificate1,
                'default_filename_formal_certificate1': applicant.filename_formal_certificate1,
                'default_formal_certificate2': applicant.formal_certificate2,
                'default_filename_formal_certificate2': applicant.filename_formal_certificate2,
                'default_formal_certificate3': applicant.formal_certificate3,
                'default_filename_formal_certificate3': applicant.filename_formal_certificate3,
                'default_informal_certificate1': applicant.informal_certificate1,
                'default_filename_informal_certificate1': applicant.filename_informal_certificate1,
                'default_informal_certificate2': applicant.informal_certificate2,
                'default_filename_informal_certificate2': applicant.filename_informal_certificate2,
                'default_informal_certificate3': applicant.informal_certificate3,
                'default_filename_informal_certificate3': applicant.filename_informal_certificate3,
                'default_informal_certificate4': applicant.informal_certificate4,
                'default_filename_informal_certificate4': applicant.filename_informal_certificate4,
                'default_informal_certificate5': applicant.informal_certificate5,
                'default_filename_informal_certificate5': applicant.filename_informal_certificate5,
                'default_academic_transcript1': applicant.academic_transcript1,
                'default_filename_academic_transcript1': applicant.filename_academic_transcript1,
                'default_academic_transcript2': applicant.academic_transcript2,
                'default_filename_academic_transcript2': applicant.filename_academic_transcript2,
                'default_academic_transcript3': applicant.academic_transcript3,
                'default_filename_academic_transcript3': applicant.filename_academic_transcript3,
            })
        context.update(vals)
        return res

    def action_send_offering_latter(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template = self.env.ref('forecastle_hr.email_template_send_offering_letter')
        ctx = {
            'default_model': 'hr.applicant',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template.id),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'force_email': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }
