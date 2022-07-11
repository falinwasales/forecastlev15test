# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError, ValidationError, UserError
from odoo.http import request
from werkzeug.exceptions import NotFound
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment
from odoo.addons.website.controllers import form
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _
from odoo.addons.base.models.ir_qweb_fields import nl2br

import base64
import json
import pytz

from datetime import datetime
from psycopg2 import IntegrityError
from werkzeug.exceptions import BadRequest


class WebsiteHrRecruitment(WebsiteHrRecruitment):
    @http.route('''/jobs/apply/<model("hr.job"):job>''', type='http', auth="public", website=True, sitemap=True)
    def jobs_apply(self, job, **kwargs):
        # res = super().jobs_apply(job, **kwargs)
        # return res
        if not job.can_access_from_current_website():
            raise NotFound()

        error = {}
        default = {}
        if 'website_hr_recruitment_error' in request.session:
            error = request.session.pop('website_hr_recruitment_error')
            default = request.session.pop('website_hr_recruitment_default')

        country = request.env.ref('base.id')
        ethnicity_ids = request.env['fce.hr.ethnicity'].sudo().search([])
        country_ids = request.env['res.country'].search([])
        location_ids = request.env['res.country.state'].search([('country_id', '=', country.id)])
        return request.render("website_hr_recruitment.apply", {
            'job': job,
            'ethnicity_ids': ethnicity_ids,
            'country_ids': country_ids,
            'location_ids': location_ids,
            'error': error,
            'default': default,
        })


class WebsiteForm(form.WebsiteForm):

    # Extract all data sent by the form and sort its on several properties
    def extract_data(self, model, values):
        dest_model = request.env[model.sudo().model]

        data = {
            'record': {},        # Values to create record
            'attachments': [],  # Attached files
            'custom': '',        # Custom fields values
            'meta': '',         # Add metadata if enabled
        }

        authorized_fields = model.sudo()._get_form_writable_fields()
        error_fields = []
        custom_fields = []

        for field_name, field_value in values.items():
            # If the value of the field if a file
            if hasattr(field_value, 'filename'):
                # Undo file upload field name indexing
                field_name = field_name.split('[', 1)[0]

                # If it's an actual binary field, convert the input file
                # If it's not, we'll use attachments instead
                if field_name in authorized_fields and authorized_fields[field_name]['type'] == 'binary':
                    data['record'][field_name] = base64.b64encode(field_value.read())
                    field_value.stream.seek(0) # do not consume value forever
                    if authorized_fields[field_name]['manual'] and field_name + "_filename" in dest_model:
                        data['record'][field_name + "_filename"] = field_value.filename
                else:
                    field_value.field_name = field_name
                    data['attachments'].append(field_value)

            # If it's a known field
            elif field_name in authorized_fields:
                try:
                    input_filter = self._input_filters[authorized_fields[field_name]['type']]
                    if field_name == 'salary_expected':
                        field_value = float(field_value.replace(',', ''))
                    if field_name == 'experience_salary_history1':
                        field_value = float(field_value.replace(',', ''))
                    if field_name == 'experience_salary_history2':
                        field_value = float(field_value.replace(',', ''))
                    if field_name == 'experience_salary_history3':
                        field_value = float(field_value.replace(',', ''))
                    data['record'][field_name] = input_filter(self, field_name, field_value)
                except ValueError:
                    error_fields.append(field_name)

            # If it's a custom field
            elif field_name != 'context':
                custom_fields.append((field_name, field_value))

        data['custom'] = "\n".join([u"%s : %s" % v for v in custom_fields])

        # Add metadata if enabled  # ICP for retrocompatibility
        if request.env['ir.config_parameter'].sudo().get_param('website_form_enable_metadata'):
            environ = request.httprequest.headers.environ
            data['meta'] += "%s : %s\n%s : %s\n%s : %s\n%s : %s\n" % (
                "IP"                , environ.get("REMOTE_ADDR"),
                "USER_AGENT"        , environ.get("HTTP_USER_AGENT"),
                "ACCEPT_LANGUAGE"   , environ.get("HTTP_ACCEPT_LANGUAGE"),
                "REFERER"           , environ.get("HTTP_REFERER")
            )

        # This function can be defined on any model to provide
        # a model-specific filtering of the record values
        # Example:
        # def website_form_input_filter(self, values):
        #     values['name'] = '%s\'s Application' % values['partner_name']
        #     return values
        if hasattr(dest_model, "website_form_input_filter"):
            data['record'] = dest_model.website_form_input_filter(request, data['record'])

        missing_required_fields = [label for label, field in authorized_fields.items() if field['required'] and not label in data['record']]
        if any(error_fields):
            raise ValidationError(error_fields + missing_required_fields)

        return data