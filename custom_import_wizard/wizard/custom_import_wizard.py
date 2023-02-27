"""
    Copyright 2020 VentorTech OU
    License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).
"""

# Stdlib:
import binascii
import io
import logging
from collections import defaultdict

# Odoo:
from odoo import _, fields, models
from odoo.exceptions import ValidationError

# Thirdparty:
import xlrd

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

_logger = logging.getLogger(__name__)

IMPORT_STATUSES = ["success", "error", "duplicate"]


class CustomImportWizard(models.TransientModel):
    """ Allows you to import records without duplicates and errors """

    _name = "custom.import.wizard"
    _description = "Custom Import Wizard"

    original_file = fields.Binary()
    original_file_name = fields.Char()
    result_file = fields.Binary()
    result_file_name = fields.Char()
    sample_file = fields.Binary()

    def read_original_file(self, no_convert_indexes=None):
        """ Get data from imported file """

        if no_convert_indexes is None:
            no_convert_indexes = []
        if not self.original_file:
            raise ValidationError('No file!')
        book = xlrd.open_workbook(
            file_contents=binascii.a2b_base64(self.original_file) or b""
        )
        sheet = book.sheet_by_index(0)
        lines = []
        for row_no in range(1, sheet.nrows):
            row = sheet.row(row_no)
            if all([not str(cell.value).strip() for cell in row]):
                continue
            lines.append(self.read_original_line(row))
        return lines

    # pylint: disable=no-self-use
    def read_original_line(self, row):
        """ This method is for formatting raw data from a cell """

        line = {"values": [], "errors": [], "status": "success"}
        for cell in row:
            line["values"].append(str(cell.value))
        return line

    # pylint: disable=no-self-use
    def _get_formats(self):
        return {
            "header": {"align": "center", "bold": True, "font_size": "10px"},
            "success": {"font_size": "8px"},
            "error": {"font_size": "8px", "bg_color": "#fccfac"},
            "duplicate": {"font_size": "8px", "bg_color": "#f29d9d"},
        }

    def write_result_file(self, headers, lines):
        """
            Writes result XLSX file
            Arguments:
                headers {list} -- List of column headers ['Company Name', 'Email']
                ]
                lines {list} -- List of dictionaries [
                    {
                        'values': ['My Company', 'test@example.com'],
                        'errors': [],
                        'status': 'success'
                    },
                    {
                        'values': ['Mega LLC', 'mega@example.com'],
                        'errors': ['Error 1', 'Error 2'],
                        'status': 'error'
                    },
                ]
        """
        with io.BytesIO() as output:
            with xlsxwriter.Workbook(output, {"in_memory": True}) as workbook:
                sheet = workbook.add_worksheet()
                sheet.set_column(0, 12, 30)

                col = row = 0
                # Write headers
                for header in headers:
                    sheet.write(row, col, header)
                    col += 1

                def _write_lines_by_status(lines_by_status, row):
                    for line in lines_by_status:
                        row += 1
                        col = 0
                        # Write line values
                        for val in line["values"]:
                            sheet.write(row, col, val)
                            col += 1
                        # Write Status
                        sheet.write(row, col, line["status"])
                        # Write Errors
                        col += 1
                        sheet.write(row, col, "; ".join(line["errors"]))

                    return row

                for status in IMPORT_STATUSES:
                    row = _write_lines_by_status(
                        filter(lambda l, st=status: l["status"] == st, lines), row
                    )

            output.seek(0)
            self.result_file = binascii.b2a_base64(output.read())
            self.result_file_name = self.original_file_name.replace(
                ".xlsx", "_formatted.xlsx"
            )

    def download_result_file(self):
        """ Downloading file from odoo field"""

        return {
            "name": "Result File",
            "type": "ir.actions.act_url",
            "url": (
                "/web/content/?model={model}&id={id}&field=result_file&"
                "download=true&filename={fname}"
            ).format(model=self._name, id=self.id, fname=self.result_file_name),
            "target": "new",
        }

    # pylint: disable=no-self-use
    def _get_model_name(self):
        return ""

    # pylint: disable=no-self-use
    def _get_extra_info(self):
        return ""

    def create_import_history(self, totals):
        """
            Creating history for created lines

            Arguments:
                totals {dict}

            Returns:
                record("custom.import.history") -- history of created records
        """

        return self.env["custom.import.history"].create(
            {
                "original_file": self.original_file,
                "formatted_file": self.result_file,
                "original_file_name": self.original_file_name,
                "formatted_file_name": self.result_file_name,
                "extra_info": self._get_extra_info(),
                "total_imported": totals.get("success", 0),
                "total_duplicated": totals.get("duplicate", 0),
                "total_errors": totals.get("error", 0),
                "model": self._get_model_name(),
            }
        )

    # pylint: disable=no-self-use,unused-argument
    def handle_import(self, test=True):
        """
            Inherit and override this method in child model

            Arguments:
                totals {boolean} -- indicates test import

            Returns:
                {list} -- list of lines
        """
        return []

    def test_import(self):
        """ Download formatted file without importing correct records to db """

        self.handle_import()
        return self.download_result_file()

    # pylint: disable=no-self-use
    def get_totals(self, lines):
        """
            Count totals of imported lines splited by import statuses
        """
        res = defaultdict(int)
        for line in lines:
            res[line["status"]] += 1
        return res

    def final_import(self):
        """ Importing correct record """

        lines = self.handle_import(test=False)
        import_history_record = self.create_import_history(self.get_totals(lines))
        context = {
            "default_message": _(
                "Successfully imported: {} | "
                "Duplicates not imported: {} | Error importing (bad info): {}"
            ).format(
                import_history_record.total_imported,
                import_history_record.total_duplicated,
                import_history_record.total_errors,
            )
        }
        return {
            "name": "Import Leads Info",
            "type": "ir.actions.act_window",
            "res_model": "info.result.import.wizard",
            "view_mode": "form",
            "view_type": "form",
            "target": "new",
            "context": context,
        }

    # pylint: disable=no-self-use
    def _get_sample_file_path(self):
        """
            Inherit and override this method in child models
            Return a path the sample xlsx file that will be returned to the user
        """
        return ""

    def print_sample_xlsx(self):
        """ Print sample file how to should be created leads """

        xlsx_file_path = self._get_sample_file_path()
        file_content = open(xlsx_file_path, "rb").read()
        self.sample_file = binascii.b2a_base64(file_content)
        return {
            "name": "Sample File",
            "type": "ir.actions.act_url",
            "url": (
                "/web/content/?model={model}&id={id}&field=sample_file&"
                "download=true&filename={fname}"
            ).format(model=self._name, id=self.id, fname="Sample Import.xlsx"),
            "target": "new",
        }
