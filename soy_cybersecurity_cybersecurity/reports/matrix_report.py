# -*- coding: utf-8 -*-
import base64
import io
from datetime import date, datetime
from math import ceil

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from PIL import Image


class IndividualReport(models.AbstractModel):
    _name = 'report.cyber_matrix_assets.report'
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
                sheet.set_column(0, 0, 5)  # nro
                sheet.set_column(1, 1, 16)  # fuente
                sheet.set_column(2, 2, 16)
                sheet.set_column(3, 3, 16)
                sheet.set_column(4, 4, 25) # description
                sheet.set_column(5, 5, 16)
                sheet.set_column(6, 9, 12)
                sheet.set_column(10, 10, 16)
                sheet.set_column(11, 13, 20)
                sheet.set_column(14, 16, 17) # evaluation
                sheet.set_column(17, 17, 11)
                sheet.set_column(18, 18, 20) # actions

                # Set row height (ALTO DE FILAS)
                sheet.set_row(3, 25)
                sheet.set_row(4, 25)

                sheet.merge_range(prod_row-1, i, prod_row,
                                  i, 'N°', format21_c_bold)
                i += 1
                sheet.merge_range(prod_row-1, i, prod_row, i,
                                  'PROCESO', format21_c_bold)
                i += 1
                sheet.merge_range(prod_row-1, i, prod_row, i,
                                  'NOMBRE DEL ACTIVO', format21_c_bold)
                i += 1
                sheet.merge_range(prod_row-1, i, prod_row, i,
                                  'ÁREA', format21_c_bold)
                

                sheet.merge_range(
                    'C1:D3', self.env.company.name, format21_c_bold)

                company_id = self.env.user.company_id

                buf_image = io.BytesIO(base64.b64decode(company_id.logo))
                im = Image.open(buf_image)
                width, height = im.size
                image_width = width
                image_height = height
                cell_width = 159.0
                cell_height = 58.0

                x_scale = cell_width/image_width
                y_scale = cell_height/image_height
                sheet.insert_image('A1', "logo.png", {
                    'image_data': buf_image, 'x_scale': x_scale, 'y_scale': y_scale})

                i += 1

                #Title 
                #var_type = "Riesgo" if matrix.type == "risk" else "Oportunidad"
                #var_type += ' ' + matrix.system_id.name if matrix.system_id else ''
                sheet.merge_range(prod_row-4, i, prod_row-2,
                                  i+11, matrix.name, format26_c_bold)
                

                sheet.merge_range(prod_row-1, i, prod_row,
                                  i, 'DESCRIPCIÓN DE ACTIVO', format21_c_bold)
                i += 1
                sheet.merge_range(prod_row-1, i, prod_row, i,
                                  'UBICACIÓN', format21_c_bold)
                i += 1
                sheet.merge_range(prod_row-1, i, prod_row, i,
                                  'RESPONSABLE', format21_c_bold)
                i += 1
                sheet.merge_range(prod_row-1, i, prod_row, i,
                                  'IDIOMA', format21_c_bold)
                i += 1
                sheet.merge_range(prod_row-1, i, prod_row,
                                  i, 'RECURSOS', format21_c_bold)
                i += 1
                sheet.merge_range(prod_row-1, i, prod_row, i,
                                  'TIPO', format21_c_bold)
                i += 1
                sheet.merge_range(prod_row-1, i, prod_row, i,
                                  'MEDIO DE CONSERVACIÓN', format21_c_bold)
                i += 1
                sheet.merge_range(prod_row-1, i, prod_row, i,
                                  'EL ACTIVO CONTIENE DATOS PERSONALES', format21_c_bold)
                i += 1
                sheet.merge_range(prod_row-1, i, prod_row, i,
                                  'EL ACTIVO ES SUSCEPTIBLE A FRAUDE O CORRUPCIÓN', format21_c_bold)
                i += 1
                sheet.merge_range(prod_row-1, i, prod_row, i,
                                  'EL ACTIVO ES VITAL PARA LA OPERACIÓN DE LA EMPRESA', format21_c_bold)
                i += 1

                # EVALUATION
                sheet.merge_range(prod_row-1, i, prod_row-1, i+2,
                                  'EVALUACIÓN', format21_c_bold)
                

                sheet.write(prod_row, i, 'CONFIDENCIALIDAD', format21_gray_bold)
                i += 1
                sheet.write(prod_row, i, 'INTEGRIDAD', format21_gray_bold)
                i += 1
                sheet.write(prod_row, i, 'DISPONIBILIDAD', format21_gray_bold)
                i += 1

                sheet.merge_range(prod_row-1, i, prod_row,
                                  i, 'VALOR DE ACTIVO', format21_c_bold)
                i += 1
                sheet.merge_range(prod_row-1, i, prod_row, i,
                                  'ACCIONES', format21_c_bold)
                


                sheet.merge_range(prod_row-4, i-2, prod_row-4,
                                  i, 'Código: '+str(matrix.code), format21_c_bold)
                sheet.merge_range(prod_row-3, i-2, prod_row-3, i,
                                  'Edición: '+str(matrix.version), format21_c_bold)
                
                sheet.merge_range(prod_row-2, i-2, prod_row-2, i, 'Fecha de aprobación: '+str(
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

                
                # MATRIX CONTENT
                
                prod_row += 1
                count = 1

                lines_order = self.env['cyber_matrix.block.line'].search(
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

                    sheet.write(prod_row, i, count, format21_left)
                    i += 1

                    sheet.write(prod_row, i,
                                line.process_id.name, format21_left)
                    i += 1

                    sheet.write(prod_row, i, line.name, format21_left)
                    i += 1

                    sheet.write(
                        prod_row, i, line.department_id.name, format21_left)
                    i += 1
                    sheet.write(prod_row, i, line.description, format21_left)
                    i += 1

                    # Many2many field
                    location_names = ', '.join(location.name for location in line.location_id)
                    sheet.write(prod_row, i, location_names, format21_left)
                    i += 1

                    sheet.write(prod_row, i, line.user_id.name, format21_left)
                    i += 1

                    language_names = ', '.join(language.name for language in line.language_id)
                    sheet.write(prod_row, i, language_names, format21_left)
                    i += 1

                    resource_names = ', '.join(resource.name for resource in line.resource_id)
                    sheet.write(prod_row, i, resource_names, format21_left)
                    i += 1

                    # Many2many field
                    asset_type_names = ', '.join(asset_type.name for asset_type in line.asset_type_id)
                    sheet.write(prod_row, i, asset_type_names, format21_left)
                    i += 1
                    
                    # Selection field
                    storage_medium_label = dict(line._fields['storage_medium'].selection).get(line.storage_medium, ' ')
                    sheet.write(prod_row, i, storage_medium_label, format21_left)
                    i += 1

                    sheet.write(prod_row, i, line.asset_contains_personal_data, format21_left)
                    i += 1
                    
                    sheet.write(prod_row, i, line.asset_susceptible_to_fraud, format21_left)
                    i += 1                   
                    sheet.write(prod_row, i, line.asset_vital_for_organization, format21_left)
                    i += 1

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


