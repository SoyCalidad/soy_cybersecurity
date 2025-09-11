# -*- coding: utf-8 -*-
import base64
import io
import os
import time
from datetime import datetime
from PIL import Image
import logging 

from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


_logger = logging.getLogger(__name__)

class DocumentaryControlReportXLS(models.AbstractModel):
    _inherit = 'report.mgmtsystem_process.documentary_control_xls'
    _description = 'Reporte de lista maestra'

    def generate_xlsx_report(self, workbook, data, records):
        """Generate a xls report with the data

        Arguments:
            workbook {object} -- A object that represents a Excel workbook
            data {dict} -- The data of the report
            partners {object} -- A class object

        Raises:
            UserError: When the user choose a initial balance but no a initial date
        """
        format_title = workbook.add_format(
            {'font_size': 13, 'font_name': 'Arial', 'valign': 'vcenter', 'bold': True, 'align': 'center',
             'border': True, 'bg_color': '#EEEEEE'})
        format_data = workbook.add_format(
            {'font_size': 9, 'font_name': 'Arial', 'valign': 'vcenter', 'align': 'center', 'border': True,
             'text_wrap': True})
        format_header = workbook.add_format(
            {'font_size': 10, 'font_name': 'Arial', 'valign': 'vcenter', 'border': True, 'text_wrap': True,
             'bold': True, 'align': 'center', 'bg_color': '#EEEEEE'})
        format_text = workbook.add_format(
            {'font_size': 10, 'font_name': 'Arial', 'border': True, 'align': 'center', 'text_wrap': True,
             'valign': 'vcenter'})

        sheet = workbook.add_worksheet('Lista Maestra')

        if not records:
            records = self.env['documentary.control'].search([])

        sheet.set_column('A:A', 20)
        sheet.set_column('C:C', 20)
        sheet.set_column('E:J', 25)
        sheet.set_column('B:B', 20)
        sheet.set_column('D:D', 20)
        sheet.set_row(4, 25)

        #company_id = self.env.company
        company_id = self.env.context.get("company_id")
        _logger.info(f"company_id by context {company_id}")
        company_id = self.env["res.company"].browse(company_id) if company_id else self.env.company

        _logger.info(f"Company id : {company_id}")
        current_master_list = self.env['documentary.control'].search([
            ('company_id', '=', company_id.id), 
            ('model_id', '=', 'documentary.control'),
        ], limit=1)
        code_master_list = ''
        _logger.info(f"master list {current_master_list}")
        if current_master_list:
            code_master_list = current_master_list.code

        buf_image = io.BytesIO(base64.b64decode(company_id.logo))
        im = Image.open(buf_image)
        width, height = im.size
        image_width = width
        image_height = height
        cell_width = 48.0
        cell_height = 48.0

        x_scale = cell_width / image_width
        y_scale = cell_height / image_height
        sheet.insert_image('A1', "logo.png", {
            'image_data': buf_image, 'x_scale': x_scale, 'y_scale': y_scale})
        sheet.merge_range('B1:I4', 'Lista maestra', format_title)
        sheet.merge_range('J1:J2', datetime.today().strftime('%d/%m/%Y'), format_title)
        sheet.merge_range('J3:J4', f"Código: {code_master_list}", format_title)
        

        sheet.write(5, 0, 'Código del proceso', format_header)
        sheet.write(5, 1, 'Procedimiento', format_header)
        sheet.write(5, 2, 'Edición vigente', format_header)
        sheet.write(5, 3, 'Registro', format_header)
        sheet.write(5, 4, 'Edición', format_header)
        sheet.write(5, 5, 'Código', format_header)
        sheet.write(5, 6, 'Área responsable', format_header)
        sheet.write(5, 7, 'Tipo de almacenamiento', format_header)
        sheet.write(5, 8, 'Tipo', format_header)
        sheet.write(5, 9, 'Clase', format_header)

        entrie_row = 6
        code = ''
        ids_company = []
        for doc in records.sudo():
            sheet.write(entrie_row, 0, doc.process_code, format_data)
            sheet.write(entrie_row, 1, doc.process_id.name, format_data)
            sheet.write(entrie_row, 2, doc.process_last_edition, format_data)
            sheet.write(entrie_row, 3, doc.name, format_data)
            sheet.write(entrie_row, 4, doc.process_last_edition, format_data)
            sheet.write(entrie_row, 5, doc.code, format_data)
            sheet.write(entrie_row, 6, doc.department_id.name, format_data)
            sheet.write(entrie_row, 7, doc.type_storage, format_data)
            sheet.write(entrie_row, 8, doc.type, format_data)
            sheet.write(entrie_row, 9, doc.clazz_id.name or '', format_data)
            sheet.set_row(entrie_row, 30)
            if doc.process_last_edition and doc.process_last_edition > code:
                code = doc.process_last_edition
            entrie_row += 1
            if doc.company_id and not code_master_list:
                ids_company.append(doc.company_id.id)
        _logger.info(f"ids_company {ids_company}")
        if len(ids_company)>0:
            current_master_list = self.env['documentary.control'].search([
                ('company_id', 'in', ids_company), 
                ('model_id', '=', 'documentary.control'),
            ], limit=1)
            _logger.info(f"master list {current_master_list}")
            if current_master_list:
                code_master_list = current_master_list.code
            sheet.merge_range('J3:J4', f"Código: {code_master_list}", format_title)

        workbook.close()
