from openpyxl import load_workbook
import re
from swagger_server.model import SubmissionsManifest, SubmissionsSample


def clean_cell(value):
    if value is None:
        return None
    value = str(value)
    value = re.sub(r"\s+", ' ', value)
    value = re.sub(r"\s+$", '', value)
    value = re.sub(r"^\s+", '', value)
    return value


def get_columns(sheet):
    if not hasattr(get_columns, "columns"):
        get_columns.columns = {}  # it doesn't exist yet, so initialize it
        row = sheet[1]
        for cell in row:
            if cell.value != "":
                get_columns.columns[cell.value] = cell.column - 1
    return get_columns.columns


def find_column(sheet, column_heading):
    columns = get_columns(sheet)
    if column_heading in columns:
        return columns[column_heading]

    return None  # Couldn't find the column


def cell_value(sheet, row, column_heading):
    column_index = find_column(sheet, column_heading)
    if column_index is None:
        return ""
    return clean_cell(row[column_index])


def read_excel(dirname=None, filename=None,
               user=None, project_name=None):
    workbook = load_workbook(filename=dirname+'/'+filename)
    sheet = workbook.active

    manifest = SubmissionsManifest()
    if project_name is not None:
        manifest.project_name = project_name
    manifest.user = user

    current_row = 2
    for row in sheet.iter_rows(min_row=current_row,
                               max_row=sheet.max_row, values_only=True):
        # Only read in rows that have a value in the SERIES column
        if cell_value(sheet, row, "SERIES") is not None:
            sample = SubmissionsSample()
            sample.manifest = manifest

            sample.row = current_row - 1
            sample.specimen_id = cell_value(sheet, row, "SPECIMEN_ID")
            sample.taxonomy_id = int(cell_value(sheet, row, "TAXON_ID"))
            sample.scientific_name = cell_value(sheet, row, "SCIENTIFIC_NAME")
            sample.family = cell_value(sheet, row, "FAMILY")
            sample.genus = cell_value(sheet, row, "GENUS")
            sample.order_or_group = cell_value(sheet, row, "ORDER_OR_GROUP")
            sample.common_name = cell_value(sheet, row, "COMMON_NAME")
            sample.lifestage = cell_value(sheet, row, "LIFESTAGE")
            sample.sex = cell_value(sheet, row, "SEX")
            sample.organism_part = cell_value(sheet, row, "ORGANISM_PART")
            sample.GAL = cell_value(sheet, row, "GAL")
            sample.GAL_sample_id = cell_value(sheet, row, "GAL_SAMPLE_ID")
            sample.collected_by = cell_value(sheet, row, "COLLECTED_BY")
            sample.collector_affiliation = cell_value(sheet, row, "COLLECTOR_AFFILIATION")
            date_of_collection = cell_value(sheet, row, "DATE_OF_COLLECTION")
            if date_of_collection is not None:
                # Only the date part
                sample.date_of_collection = date_of_collection.partition(' ')[0]
            sample.collection_location = cell_value(sheet, row, "COLLECTION_LOCATION")
            sample.decimal_latitude = cell_value(sheet, row, "DECIMAL_LATITUDE")
            sample.decimal_longitude = cell_value(sheet, row, "DECIMAL_LONGITUDE")
            sample.habitat = cell_value(sheet, row, "HABITAT")
            sample.identified_by = cell_value(sheet, row, "IDENTIFIED_BY")
            sample.identifier_affiliation = cell_value(sheet, row, "IDENTIFIER_AFFILIATION")
            sample.voucher_id = cell_value(sheet, row, "VOUCHER_ID")
            sample.elevation = cell_value(sheet, row, "ELEVATION")
            sample.depth = cell_value(sheet, row, "DEPTH")
            sample.relationship = cell_value(sheet, row, "RELATIONSHIP")
            sample.symbiont = cell_value(sheet, row, "SYMBIONT")
            sample.culture_or_strain_id = cell_value(sheet, row, "CULTURE_OR_STRAIN_ID")

        current_row += 1
    return manifest
