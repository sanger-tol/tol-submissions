# SPDX-FileCopyrightText: 2021 Genome Research Ltd.
#
# SPDX-License-Identifier: MIT

import shutil
import xml.etree.ElementTree as ET
import tempfile
import os


def build_bundle_sample_xml(manifest):
    '''build structure and save to file bundle_file_subfix.xml'''
    dir = tempfile.TemporaryDirectory()

    filename = dir.name + "bundle_" + str(manifest.manifest_id) + ".xml"
    shutil.copy("main/templates/sample.xml", filename)
    update_bundle_sample_xml(manifest, filename)
    return filename


def update_bundle_sample_xml(manifest, bundlefile):
    '''update the sample with submission alias adding a new sample'''
    # print("adding sample to bundle sample xml")
    tree = ET.parse(bundlefile)
    root = tree.getroot()
    for sample in manifest.samples:
        sample_alias = ET.SubElement(root, 'SAMPLE')
        sample_alias.set('alias', str(sample.sample_id))
        sample_alias.set('center_name', 'SangerInstitute')
        title = str(sample.sample_id) + "-tol"

        title_block = ET.SubElement(sample_alias, 'TITLE')
        title_block.text = title
        sample_name = ET.SubElement(sample_alias, 'SAMPLE_NAME')
        taxon_id = ET.SubElement(sample_name, 'TAXON_ID')
        taxon_id.text = str(sample.taxonomy_id)
        sample_attributes = ET.SubElement(sample_alias, 'SAMPLE_ATTRIBUTES')

        ena_fields = sample.to_ena_dict()
        for item in ena_fields:
            sample_attribute = ET.SubElement(sample_attributes, 'SAMPLE_ATTRIBUTE')
            tag = ET.SubElement(sample_attribute, 'TAG')
            tag.text = item
            value = ET.SubElement(sample_attribute, 'VALUE')
            value.text = str(ena_fields[item]["value"])
            # add ena units where necessary
            if "units" in ena_fields[item]:
                unit = ET.SubElement(sample_attribute, 'UNITS')
                unit.text = ena_fields[item]["units"]

    ET.dump(tree)
    tree.write(open(bundlefile, 'w'),
               encoding='unicode')


def build_submission_xml(manifest):
    # build submission XML
    tree = ET.parse("main/templates/submission.xml")
    root = tree.getroot()
    # set submission attributes
    # root.set("submission_date", datetime.utcnow()
    #   .replace(tzinfo=d_utils.simple_utc()).isoformat())

    # set SRA contacts
    contacts = root.find('CONTACTS')

    # set copo sra contacts
    copo_contact = ET.SubElement(contacts, 'CONTACT')
    copo_contact.set("name", os.getenv("ENA_CONTACT_NAME"))
    copo_contact.set("inform_on_error", os.getenv("ENA_CONTACT_EMAIL"))
    copo_contact.set("inform_on_status", os.getenv("ENA_CONTACT_EMAIL"))
    ET.dump(tree)
    dir = tempfile.TemporaryDirectory()

    submissionfile = dir.name + "submission_" + str(manifest.manifest_id) + ".xml"

    tree.write(open(submissionfile, 'w'),
               encoding='unicode')

    return submissionfile
