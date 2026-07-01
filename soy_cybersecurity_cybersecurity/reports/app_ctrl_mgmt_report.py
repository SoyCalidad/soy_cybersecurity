# -*- coding: utf-8 -*-
import base64
import io
from datetime import date, datetime
from math import ceil

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from PIL import Image
import logging 
import re

_logger = logging.getLogger(__name__)

class IndividualReport(models.AbstractModel):
    _name = 'report.cyber_2matrix_matrix.report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, matrixes):
        try:
            format21_c_bold = workbook.add_format(
                {'font_size': 10, 'bg_color': '#595959', 'align': 'center', 'valign': 'vcenter', 'bold': True, 'text_wrap': True, 'font_color': 'white'})
            format10_c_bold = workbook.add_format(
                {'font_size': 10,  'align': 'center', 'valign': 'vcenter', 'bold': True, 'text_wrap': True, })
            format21_left = workbook.add_format(
                {'font_size': 10, 'align': 'left', 'valign': 'vcenter', 'bold': False, 'text_wrap': True})
            format21_gray = workbook.add_format(
                {'font_size': 10, 'bg_color': '#EEEEEE', 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'border': True})
            format21_red = workbook.add_format(
                {'font_size': 10, 'bg_color': '#FF0000', 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'border': True})
            format21_gray_bold = workbook.add_format(
                {'font_size': 10, 'bg_color': '#EEEEEE', 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'bold': True, 'border': True })
            format21_red_bold = workbook.add_format(
                {'font_size': 10, 'bg_color': '#FF0000', 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'bold': True, 'border': True })
            format26_c_bold = workbook.add_format(
                {'font_size': 22,  'align': 'center', 'valign': 'vcenter', 'bold': True, 'text_wrap': True})

            format11_bg_dark_blue= workbook.add_format(
                {'font_size': 11, 'bg_color': '#1F4E78',  'valign': 'vcenter', 'bold': False, 'text_wrap': True, 'font_color': 'white'})
            
            date_format = workbook.add_format(
                {'font_size': 10, 'bg_color': '#A0A0A0','num_format': 'dd/mm/yyyy', 'bold': True, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
            for matrix in matrixes:
                sheet = workbook.add_worksheet(str(matrix.name or 'Sin nombre'))



                format26_c_bold.set_border()
                format21_c_bold.set_border()
                format10_c_bold.set_border()
                format21_left.set_border()
                format21_gray.set_border()
                format21_gray_bold.set_border()

                prod_row = 4
                i = 0

                # Set column width (ANCHO DE COLUMNAS)
                sheet.set_column(0, 0, 15) # numero
                sheet.set_column(1, 1, 35)  # nombre del control
                sheet.set_column(2, 2, 70) # description
                sheet.set_column(3, 3, 20) #aplicab
                sheet.set_column(4, 4, 50) 
                sheet.set_column(5, 5, 25) # app description
                sheet.set_column(6, 6, 25) # app evidence
                sheet.set_column(7, 8, 30) # Type

                # Set row height (ALTO DE FILAS)
                sheet.set_row(0, 25)
                sheet.set_row(1, 25)
                sheet.set_row(2, 25)
                sheet.set_row(4, 25)

                sheet.write(prod_row, i, 'N°', format21_c_bold)
                i += 1
                sheet.write(prod_row, i,
                                  'Nombre del control', format21_c_bold)
                i += 1
                sheet.write(prod_row, i, 'Descripción del control', format21_c_bold)
                sheet.merge_range(0, i, 2, i+2, matrix.name, format26_c_bold)       

                i += 1
                sheet.write(prod_row, i,'Aplicabilidad (SÍ/NO)', format21_c_bold)

                 
                i += 1
                sheet.write(prod_row, i,
                                  'Justificación de la aplicabilidad / no aplicabilidad', format21_c_bold)
                i += 1
                sheet.write(prod_row, i,
                                  '¿Control Implementado? (SÍ/NO)', format21_c_bold)
                i += 1
                sheet.write(prod_row, i, 'Referencia de la implementación del control', format21_c_bold)

                i += 1
                sheet.write(prod_row, i, 'Acciones', format21_c_bold)

                #xlsxwriter.exceptions.OverlappingRange: Merge range 'C1:C3' overlaps previous merge range 'C1:F3'.


                #sheet.merge_range('C1:C3', self.env.company.name, format21_c_bold)

                company_id = self.env.user.company_id

                buf_image = io.BytesIO(base64.b64decode(company_id.logo))
                im = Image.open(buf_image)
                width, height = im.size
                image_width = width
                image_height = height
                cell_width = 191.0
                cell_height = 58.0

                x_scale = cell_width/image_width
                y_scale = cell_height/image_height
                sheet.insert_image('A1', "logo.png", {
                    'image_data': buf_image, 'x_scale': x_scale, 'y_scale': y_scale})

                i += 1

                MAX_COL = 7 #CELL H


                sheet.merge_range(0, MAX_COL -2, 0,
                                  MAX_COL, f'Código: {matrix.code or ""}', format10_c_bold)
                sheet.merge_range(1, MAX_COL -2, 1, MAX_COL,
                                  'Versión: '+str(matrix.version), format10_c_bold)
                
                sheet.merge_range(2, MAX_COL -2, 2, MAX_COL, 'Fecha de validación: '+str(
                    matrix.date_validate or "Sin definir"), format10_c_bold) # old date_validate
            
                
                # REPORT DATA CONTENT
                
                prod_row += 1

                lines = matrix.line_ids

                row_count = 1
                row_a = 0
                max_height = 20

                from collections import defaultdict
                group_lines = defaultdict(list)

                for line in lines:
                    group_lines[line.applicability_id_domain_id].append(line)

                for domain, lines in group_lines.items():
                    sheet.merge_range(prod_row, 0, prod_row, MAX_COL, f"{domain.name.upper()} {domain.description.upper() if domain.description else ''}", format11_bg_dark_blue)
                    sheet.set_row(prod_row, 25)
                    prod_row += 1 
                    for line in lines:
                        # sheet.set_row(prod_row, 25)

                        i = 0

                        numero = ""
                        nombre = ""
                        match = re.match(r'^(\d+(?:\.\d+)?)\s+(.*)$', line.applicability_id_name or '')
                        if match:
                            numero = match.group(1)   # "5.1"
                            nombre = match.group(2)

                        sheet.write(prod_row, i, numero, format21_left)
                        i += 1

                        sheet.write(prod_row, i, nombre, format21_left)
                        i += 1

                        sheet.write(prod_row, i, line.applicability_id_description_application or '', format21_left)
                        i += 1

                        sheet.write(prod_row, i, "SÍ" if line.applicability_id_application else "NO", format21_left)
                        i += 1

                        sheet.write(prod_row, i, line.justification or '', format21_left)
                        i += 1

                        sheet.write(prod_row, i, "SÍ" if line.is_implemented else "NO", format21_left)
                        i += 1


                        sheet.write(prod_row, i, line.reference or '', format21_left)
                        i += 1                    

                        actions_name = "\n".join([action.display_name for action in line.action_ids])
                        sheet.write(prod_row, i, actions_name, format21_left)
                        

                        prod_row += 1
                    

        except Exception as e:
            _logger.warning(str(e))
            raise UserError("Hubo un error al generar el reporte")


