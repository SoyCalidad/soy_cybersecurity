# -*- coding: utf-8 -*-
import base64
import io
from datetime import date, datetime
from math import ceil

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from PIL import Image


class IndividualReport(models.AbstractModel):
    _name = 'report.cyber_2matrix_matrix.report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, matrixes):
        try:
            for matrix in matrixes:
                sheet = workbook.add_worksheet(str(matrix.name))

                format21_c_bold = workbook.add_format(
                    {'font_size': 10, 'bg_color': '#A0A0A0', 'align': 'center', 'valign': 'vcenter', 'bold': True, 'text_wrap': True})
                format21_left = workbook.add_format(
                    {'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'bold': False, 'text_wrap': True})
                format21_gray = workbook.add_format(
                    {'font_size': 10, 'bg_color': '#EEEEEE', 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'border': True})
                format21_red = workbook.add_format(
                    {'font_size': 10, 'bg_color': '#FF0000', 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'border': True})
                format21_gray_bold = workbook.add_format(
                    {'font_size': 10, 'bg_color': '#EEEEEE', 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'bold': True, 'border': True })
                format21_red_bold = workbook.add_format(
                    {'font_size': 10, 'bg_color': '#FF0000', 'align': 'center', 'valign': 'vcenter', 'text_wrap': True, 'bold': True, 'border': True })
                format26_c_bold = workbook.add_format(
                    {'font_size': 26, 'bg_color': '#A0A0A0', 'align': 'center', 'valign': 'vcenter', 'bold': True, 'text_wrap': True})
                
                date_format = workbook.add_format(
                    {'font_size': 10, 'bg_color': '#A0A0A0','num_format': 'dd/mm/yyyy', 'bold': True, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True})


                format26_c_bold.set_border()
                format21_c_bold.set_border()
                format21_left.set_border()
                format21_gray.set_border()
                format21_gray_bold.set_border()

                prod_row = 4
                i = 0

                # Set column width (ANCHO DE COLUMNAS)
                sheet.set_column(0, 0, 10) # Domain
                sheet.set_column(1, 1, 16)  
                sheet.set_column(2, 2, 25) # Control target
                sheet.set_column(3, 3, 20)
                sheet.set_column(4, 4, 12) 
                sheet.set_column(5, 5, 25) # app description
                sheet.set_column(6, 6, 25) # app evidence
                sheet.set_column(7, 8, 14) # Type

                # Set row height (ALTO DE FILAS)
                sheet.set_row(3, 25)
                sheet.set_row(4, 25)

                sheet.merge_range(prod_row-1, i, prod_row,
                                  i, 'Dominio', format21_c_bold)
                i += 1
                sheet.merge_range(prod_row-1, i, prod_row, i,
                                  'Descripción', format21_c_bold)
                i += 1
                sheet.merge_range(prod_row-1, i, prod_row, i,
                                  'Objetivo de Control', format21_c_bold)
                i += 1
                sheet.merge_range(prod_row-1, i, prod_row, i,
                                  'Control', format21_c_bold)

                sheet.merge_range(prod_row-4, i, prod_row-2,
                                  i+3, matrix.name, format26_c_bold)       
                 
                i += 1
                sheet.merge_range(prod_row-1, i, prod_row, i,
                                  'Aplica', format21_c_bold)
                i += 1
                sheet.merge_range(prod_row-1, i, prod_row, i,
                                  'Descripción de Aplicación', format21_c_bold)
                i += 1
                sheet.merge_range(prod_row-1, i, prod_row, i,
                                  'Evidencia o registro de implementación', format21_c_bold)


                sheet.merge_range(
                    'C1:C3', self.env.company.name, format21_c_bold)

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

                #Title 
                #var_type = "Riesgo" if matrix.type == "risk" else "Oportunidad"
                #var_type += ' ' + matrix.system_id.name if matrix.system_id else ''


                # TYPE
                sheet.merge_range(prod_row-1, i, prod_row-1, i+1,
                                  'TIPO', format21_c_bold)
                

                sheet.write(prod_row, i, 'Nacional', format21_gray_bold)
                i += 1
                sheet.write(prod_row, i, 'Internacional', format21_gray_bold)



                sheet.merge_range(prod_row-4, i-1, prod_row-4,
                                  i, 'Código: '+str(matrix.code), format21_c_bold)
                sheet.merge_range(prod_row-3, i-1, prod_row-3, i,
                                  'Edición: '+str(matrix.version), format21_c_bold)
                
                sheet.merge_range(prod_row-2, i-1, prod_row-2, i, 'Fecha de aprobación: '+str(
                    matrix.date_validate or "Sin definir"), format21_c_bold) # old date_validate
                
                       
                '''
                if matrix.validation_step.date:
                    fecha_de_aprobacion = matrix.validation_step.date
                    # Escribe la fecha con el formato adecuado
                    sheet.write_datetime(prod_row-2, i-2, fecha_de_aprobacion, date_format)
                else:
                    # Manejar el caso cuando la fecha no está definida
                    sheet.merge_range(prod_row-2, i-2, prod_row-2, i, 'Fecha de aprobación: Sin definir', format21_c_bold)
                '''
                i += 1 
                '''
                count_cri = 0
                if matrix.line_ids:
                    if matrix.line_ids[0].evaluation_id:
                        for criterio in matrix.line_ids[0].evaluation_id.criterio_ids:
                            count_cri += 1
                            sheet.write(prod_row, i, criterio.name,
                                        format21_gray_bold)
                            i += 1
                sheet.write(prod_row, i, 'Resultado', format21_gray_bold)
                i += 1
                sheet.merge_range(prod_row-1, i-count_cri-1,
                                  prod_row-1, i-1, 'Valoración', format21_c_bold)

                sheet.merge_range(prod_row-1, i, prod_row, i,
                                  'Acciones abordadas', format21_c_bold)

                                  
                var_type = "Riesgo" if matrix.type == "risk" else "Oportunidad"
                var_type += ' ' + matrix.system_id.name if matrix.system_id else ''
                sheet.merge_range(prod_row-4, i-count_cri-4, prod_row-2,
                                  i, 'Matriz de ' + var_type, format26_c_bold)
                i += 1

                '''

                
                # REPORT DATA CONTENT
                
                prod_row += 1
                count = 1

                lines_order = self.env['cyber_2matrix.block.line'].search(
                    [('id', 'in', matrix.line_ids.ids)], order="id")

                block_name = ""
                row_count = 1
                row_a = 0
                line_actual = 0
                last_line = len(lines_order)
                max_height = 20

                for line in lines_order:
                    line_actual += 1
                    i = 0

                    if block_name == "":
                        block_name = line.name or ""
                        row_a = prod_row
                    else:
                        row_count += 1

                    #sheet.write(prod_row, i, count, format21_left)
                    #i += 1

                    sheet.write(prod_row, i,line.domain_id.name, format21_left)
                    i += 1

                    sheet.write(prod_row, i, line.domain_id.description, format21_left)
                    i += 1

                    sheet.write(
                        prod_row, i, line.ctrl_target_id.name, format21_left)
                    i += 1

                    sheet.write(prod_row, i, line.name, format21_left)
                    i += 1

                    sheet.write(prod_row, i, line.application, format21_left)
                    i += 1

                    sheet.write(prod_row, i, line.description_application, format21_left)
                    i += 1

                    sheet.write(prod_row, i, line.implementation_record, format21_left)
                    i += 1

                    
                    # Selection field

                    # TYPE OF CONTROL
                    # 1st option "national"
                    if line.type == 'national':
                        sheet.write(prod_row, i, "X", format21_left)
                    else:
                        sheet.write(prod_row, i, "", format21_left)
                    i += 1                    

                    # 2nd option "international" 
                    if line.type == 'international':
                        sheet.write(prod_row, i, "X", format21_left)
                    else:
                        sheet.write(prod_row, i, "", format21_left)
                    

                    '''
                    for result in line.result_ids:
                        if result.value >= 6:
                            sheet.write(prod_row, i, result.value,
                                        format21_gray_bold)
                        else:    
                            sheet.write(prod_row, i, result.value, format21_left)
                        i += 1
                    ntr = line.ntr or 0
                    if int(ntr) > 100:
                        sheet.write(prod_row, i, line.ntr, format21_gray_bold)
                    else:
                        sheet.write(prod_row, i, line.ntr, format21_gray_bold)
                    i += 1
                    '''

                    '''
                    
                    len_action_ids = len(
                        '\n'.join([x.name for x in line.action_ids]))
                    len_name = len(line.name)
                    len_effect = len(line.effect) if line.effect else 0
                    len_cause = len(line.cause) if line.cause else 0

                    max_height = max(len_action_ids, len_name,
                                     len_effect, len_cause)

                    if max_height > 25:
                        max_height = ceil(max_height/25)*10
                    else:
                        max_height = 20

                    sheet.set_row(prod_row, max_height)

                    for result in line.result_ids:
                        if result.value <= 5:
                            sheet.write(prod_row, i, result.value,
                                        format21_red_bold)
                        sheet.write(prod_row, i, result.value, format21_left)
                        i += 1
                    ntr = line.ntr or 0
                    if int(ntr) > 100:
                        sheet.write(prod_row, i, line.ntr, format21_red)
                    else:
                        sheet.write(prod_row, i, line.ntr, format21_gray)
                    i += 1

                    sheet.write(prod_row, i, '\n '.join(
                        x.name for x in line.action_ids), format21_left)
                    i += 1
                    sheet.write(prod_row, i, '\n '.join(
                        x.user_id.name for x in line.action_ids), format21_left)
                    i += 1
                    sheet.write(prod_row, i, '\n '.join(
                        str(x.date_open) for x in line.action_ids), format21_left)
                    i += 1
                    date_deadline = '\n '.join(x.date_deadline.strftime(
                        '%d/%m/%Y') if x.date_deadline else '' for x in line.action_ids)
                    sheet.write(prod_row, i, date_deadline, format21_left)
                    i += 1
                    '''
                    prod_row += 1
                    count += 1
                    

        except Exception as e:
            print(e)
            raise UserError("Hubo un error al generar el reporte")


