# Created by fshaw at 03/04/2020
import inspect
import math
import os
import uuid
from os.path import join, isfile
from pathlib import Path
from shutil import rmtree
from urllib.error import HTTPError

import jsonpath_rw_ext as jp
import pandas
from django.conf import settings
from django.core.files.storage import default_storage
from django_tools.middlewares import ThreadLocal

import COPO.web.apps.web_copo.schemas.utils.data_utils as d_utils
from COPO.api.utils import map_to_dict
from COPO.dal.copo_da import Sample, DataFile, Profile
from COPO.submission.helpers.generic_helper import notify_dtol_status
from COPO.web.apps.web_copo.copo_email import CopoEmail
from COPO.web.apps.web_copo.lookup import dtol_lookups as lookup
from COPO.web.apps.web_copo.lookup import lookup as lk
from COPO.web.apps.web_copo.lookup.lookup import SRA_SETTINGS
from COPO.web.apps.web_copo.schemas.utils.data_utils import json_to_pytype
from COPO.web.apps.web_copo.utils.dtol.Dtol_Helpers import make_tax_from_sample
from COPO.web.apps.web_copo.utils.dtol.tol_validators import optional_field_dtol_validators as optional_validators
from COPO.web.apps.web_copo.utils.dtol.tol_validators import required_field_dtol_validators as required_validators
from COPO.web.apps.web_copo.utils.dtol.tol_validators import taxon_validators
from COPO.web.apps.web_copo.utils.dtol.tol_validators.tol_validator import TolValidtor


def make_target_sample(sample):
    # need to pop taxon info, and add back into sample_list
    if not "species_list" in sample:
        sample["species_list"] = list()
    out = dict()
    out["SYMBIONT"] = "target"
    out["TAXON_ID"] = sample.pop("TAXON_ID")
    out["ORDER_OR_GROUP"] = sample.pop("ORDER_OR_GROUP")
    out["FAMILY"] = sample.pop("FAMILY")
    out["GENUS"] = sample.pop("GENUS")
    out["SCIENTIFIC_NAME"] = sample.pop("SCIENTIFIC_NAME")
    out["INFRASPECIFIC_EPITHET"] = sample.pop("INFRASPECIFIC_EPITHET")
    out["CULTURE_OR_STRAIN_ID"] = sample.pop("CULTURE_OR_STRAIN_ID")
    out["COMMON_NAME"] = sample.pop("COMMON_NAME")
    out["TAXON_REMARKS"] = sample.pop("TAXON_REMARKS")
    sample["species_list"].append(out)
    return sample


class DtolSpreadsheet:
    fields = ""
    sra_settings = d_utils.json_to_pytype(SRA_SETTINGS).get("properties", dict())

    def __init__(self, file=None):
        self.req = ThreadLocal.get_current_request()
        self.profile_id = self.req.session.get("profile_id", None)
        sample_images = Path(settings.MEDIA_ROOT) / "sample_images"
        display_images = Path(settings.MEDIA_ROOT) / "img" / "sample_images"
        self.these_images = sample_images / self.profile_id
        self.display_images = display_images / self.profile_id
        self.data = None
        self.required_field_validators = list()
        self.optional_field_validators = list()
        self.taxon_field_validators = list()
        self.optional_validators = optional_validators
        self.required_validators = required_validators
        self.taxon_validators = taxon_validators
        self.symbiont_list = []
        self.validator_list = []
        # if a file is passed in, then this is the first time we have seen the spreadsheet,
        # if not then we are looking at creating samples having previously validated
        if file:
            self.file = file
        else:
            self.sample_data = self.req.session.get("sample_data", "")

        # get type of manifest
        t = Profile().get_type(self.profile_id)
        if "ASG" in t:
            self.type = "ASG"
        else:
            self.type = "DTOL"

        # create list of required validators
        required = dict(globals().items())["required_validators"]
        for element_name in dir(required):
            element = getattr(required, element_name)
            if inspect.isclass(element) and issubclass(element, TolValidtor) and not element.__name__ == "TolValidtor":
                self.required_field_validators.append(element)
        # create list of optional validators
        optional = dict(globals().items())["optional_validators"]
        for element_name in dir(optional):
            element = getattr(optional, element_name)
            if inspect.isclass(element) and issubclass(element, TolValidtor) and not element.__name__ == "TolValidtor":
                self.optional_field_validators.append(element)
        # create list of taxon validators
        optional = dict(globals().items())["taxon_validators"]
        for element_name in dir(optional):
            element = getattr(optional, element_name)
            if inspect.isclass(element) and issubclass(element, TolValidtor) and not element.__name__ == "TolValidtor":
                self.taxon_field_validators.append(element)

    def loadManifest(self, m_format):

        if self.profile_id is not None:
            notify_dtol_status(data={"profile_id": self.profile_id}, msg="Loading..", action="info",
                               html_id="sample_info")
            try:
                # read excel and convert all to string
                if m_format == "xls":
                    self.data = pandas.read_excel(self.file, keep_default_na=False,
                                                  na_values=lookup.na_vals)
                elif m_format == "csv":
                    self.data = pandas.read_csv(self.file, keep_default_na=False,
                                                na_values=lookup.na_vals)
                '''
                for column in self.allowed_empty:
                    self.data[column] = self.data[column].fillna("")
                '''
                self.data = self.data.apply(lambda x: x.astype(str))
                self.data = self.data.apply(lambda x: x.str.strip())
            except Exception as e:
                # if error notify via web socket
                notify_dtol_status(data={"profile_id": self.profile_id}, msg="Unable to load file. " + str(e),
                                   action="info",
                                   html_id="sample_info")
                return False
            return True

    def validate(self):
        flag = True
        errors = []

        try:
            # get definitive list of mandatory DTOL fields from schema
            s = json_to_pytype(lk.WIZARD_FILES["sample_details"])
            self.fields = jp.match(
                '$.properties[?(@.specifications[*] == "' + self.type.lower() + '" & @.required=="true")].versions[0]',
                s)

            # validate for required fields
            for v in self.required_field_validators:
                errors, flag = v(profile_id=self.profile_id, fields=self.fields, data=self.data,
                                 errors=errors, flag=flag).validate()

            # get list of all DTOL fields from schemas
            self.fields = jp.match(
                '$.properties[?(@.specifications[*] == ' + self.type.lower() + ')].versions[0]', s)

            # validate for optional dtol fields
            for v in self.optional_field_validators:
                errors, flag = v(profile_id=self.profile_id, fields=self.fields, data=self.data,
                                 errors=errors, flag=flag).validate()

            # if flag is false, compile list of errors
            if not flag:
                errors = list(map(lambda x: "<li>" + x + "</li>", errors))
                errors = "".join(errors)

                notify_dtol_status(data={"profile_id": self.profile_id},
                                   msg="<h4>" + self.file.name + "</h4><ol>" + errors + "</ol>",
                                   action="error",
                                   html_id="sample_info")
                return False



        except Exception as e:
            error_message = str(e).replace("<", "").replace(">", "")
            notify_dtol_status(data={"profile_id": self.profile_id}, msg="Server Error - " + error_message,
                               action="info",
                               html_id="sample_info")
            return False

        # if we get here we have a valid spreadsheet
        notify_dtol_status(data={"profile_id": self.profile_id}, msg="Spreadsheet is Valid", action="info",
                           html_id="sample_info")
        notify_dtol_status(data={"profile_id": self.profile_id}, msg="", action="close", html_id="upload_controls")
        notify_dtol_status(data={"profile_id": self.profile_id}, msg="", action="make_valid", html_id="sample_info")

        return True

    def validate_taxonomy(self):
        ''' check if provided scientific name, TAXON ID,
        family and order are consistent with each other in known taxonomy'''

        errors = []
        warnings = []
        flag = True
        try:
            # validate for optional dtol fields
            for v in self.taxon_field_validators:
                errors, warnings, flag = v(profile_id=self.profile_id, fields=self.fields, data=self.data,
                                           errors=errors, flag=flag).validate()

            # send warnings
            if warnings:
                notify_dtol_status(data={"profile_id": self.profile_id},
                                   msg="<br>".join(warnings),
                                   action="warning",
                                   html_id="warning_info")

            if not flag:
                errors = list(map(lambda x: "<li>" + x + "</li>", errors))
                errors = "".join(errors)
                notify_dtol_status(data={"profile_id": self.profile_id},
                                   msg="<h4>" + self.file.name + "</h4><ol>" + errors + "</ol>",
                                   action="error",
                                   html_id="sample_info")
                return False

            else:
                return True

        except HTTPError as e:

            error_message = str(e).replace("<", "").replace(">", "")
            notify_dtol_status(data={"profile_id": self.profile_id},
                               msg="Service Error - The NCBI Taxonomy service may be down, please try again later.",
                               action="error",
                               html_id="sample_info")
            return False
        except Exception as e:
            error_message = str(e).replace("<", "").replace(">", "")
            notify_dtol_status(data={"profile_id": self.profile_id}, msg="Server Error - " + error_message,
                               action="error",
                               html_id="sample_info")
            return False

    def check_image_names(self, files):
        # compare list of sample names with specimen ids already uploaded
        samples = self.sample_data
        # get list of specimen_ids in sample
        specimen_id_column_index = 0
        output = list()
        for num, col_name in enumerate(samples[0]):
            if col_name == "SPECIMEN_ID":
                specimen_id_column_index = num
                break
        if os.path.isdir(self.these_images):
            rmtree(self.these_images)
        self.these_images.mkdir(parents=True)

        write_path = Path(self.these_images)
        display_write_path = Path(self.display_images)
        for f in files:
            file = files[f]

            file_path = write_path / file.name
            # write full sized image to large storage
            file_path = Path(settings.MEDIA_ROOT) / "sample_images" / self.profile_id / file.name
            with default_storage.open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            filename = os.path.splitext(file.name)[0].upper()
            # now iterate through samples data to see if there is a match between specimen_id and image name
        image_path = Path(settings.MEDIA_ROOT) / "sample_images" / self.profile_id
        for num, sample in enumerate(samples):
            found = False
            if num != 0:
                specimen_id = sample[specimen_id_column_index].upper()

                file_list = [f for f in os.listdir(image_path) if isfile(join(image_path, f))]
                for filename in file_list:
                    if specimen_id in filename.upper():
                        # we have a match
                        p = Path(settings.MEDIA_URL) / "sample_images" / self.profile_id / filename

                        output.append({"file_name": str(p), "specimen_id": sample[specimen_id_column_index]})
                        found = True
                        break
                if not found:
                    output.append({
                        "file_name": "None", "specimen_id": "No Image found for <strong>" + sample[
                            specimen_id_column_index] + "</strong>"
                    })
        # save to session
        request = ThreadLocal.get_current_request()
        request.session["image_specimen_match"] = output
        notify_dtol_status(data={"profile_id": self.profile_id}, msg=output, action="make_images_table",
                           html_id="images")
        return output

    def collect(self):
        # create table data to show to the frontend from parsed manifest
        sample_data = []
        headers = list()
        for col in list(self.data.columns):
            headers.append(col)
        sample_data.append(headers)
        for index, row in self.data.iterrows():
            r = list(row)
            for idx, x in enumerate(r):
                if x is math.nan:
                    r[idx] = ""
            sample_data.append(r)
        # store sample data in the session to be used to create mongo objects
        self.req.session["sample_data"] = sample_data
        notify_dtol_status(data={"profile_id": self.profile_id}, msg=sample_data, action="make_table",
                           html_id="sample_table")

    def save_records(self):
        # create mongo sample objects from info parsed from manifest and saved to session variable
        sample_data = self.sample_data
        manifest_id = str(uuid.uuid4())
        request = ThreadLocal.get_current_request()
        image_data = request.session.get("image_specimen_match", [])
        for p in range(1, len(sample_data)):
            s = (map_to_dict(sample_data[0], sample_data[p]))
            s["sample_type"] = self.type.lower()
            s["tol_project"] = self.type
            s["biosample_accession"] = []
            s["manifest_id"] = manifest_id
            s["status"] = "pending"
            s["rack_tube"] = s["RACK_OR_PLATE_ID"] + "/" + s["TUBE_OR_WELL_ID"]
            notify_dtol_status(data={"profile_id": self.profile_id},
                               msg="Creating Sample with ID: " + s["TUBE_OR_WELL_ID"] + "/" + s["SPECIMEN_ID"],
                               action="info",
                               html_id="sample_info")

            if s["SYMBIONT"].lower() == "symbiont":
                self.check_for_target_or_add_to_symbiont_list(s)
            else:
                #SOP 2.2 DTOL symbiont to be a scientific name
                s = make_target_sample(s)
                sampl = Sample(profile_id=self.profile_id).save_record(auto_fields={}, **s)
                Sample().timestamp_dtol_sample_created(sampl["_id"])
                self.add_from_symbiont_list(s)

            for im in image_data:
                # create matching DataFile object for image is provided
                if s["SPECIMEN_ID"] in im["specimen_id"]:
                    fields = {"file_location": im["file_name"]}
                    df = DataFile().save_record({}, **fields)
                    DataFile().insert_sample_id(df["_id"], sampl["_id"])
                    break;

        uri = request.build_absolute_uri('/')
        profile_id = request.session["profile_id"]
        profile = Profile().get_record(profile_id)
        title = profile["title"]
        description = profile["description"]
        CopoEmail().notify_new_manifest(uri + 'copo/accept_reject_sample/', title=title, description=description)

    def delete_sample(self, sample_ids):
        # accept a list of ids, try to delete creating report
        report = list()
        for s in sample_ids:
            r = Sample().delete_sample(s)
            report.append(r)
        notify_dtol_status(data={"profile_id": self.profile_id}, msg=report,
                           action="info",
                           html_id="sample_info")

    def add_from_symbiont_list(self, s):
        for idx, el in enumerate(self.symbiont_list):
            if el.get("RACK_OR_PLATE_ID", "") == s.get("RACK_OR_PLATE_ID", "") \
                    and el.get("TUBE_OR_WELL_ID", "") == s.get("TUBE_OR_WELL_ID", ""):
                out = self.symbiont_list.pop(idx)
                out.pop("RACK_OR_PLATE_ID")
                out.pop("TUBE_OR_WELL_ID")
                Sample().add_symbiont(s, out)

    def check_for_target_or_add_to_symbiont_list(self, s):
        # method checks if there is an existing target sample to attach this symbiont to. If so we attach, if not,
        # we create the tax data, and append to a list of use by a later sample
        if not Sample().check_and_add_symbiont(s):
            # add to list
            out = make_tax_from_sample(s)
            self.symbiont_list.append(out)
