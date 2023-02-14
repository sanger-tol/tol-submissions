# SPDX-FileCopyrightText: 2021 Genome Research Ltd.
#
# SPDX-License-Identifier: MIT

import os
import shutil
import tempfile
import xml.etree.ElementTree as ElementTree


def build_bundle_sample_xml(manifest):
    """build structure and save to file bundle_file_subfix.xml"""
    dir_ = tempfile.TemporaryDirectory()

    filename = dir_.name + 'bundle_' + str(manifest.manifest_id) + '.xml'
    shutil.copy('main/templates/sample.xml', filename)
    sample_count = update_bundle_sample_xml(manifest, filename)
    return filename, sample_count


def update_bundle_sample_xml(manifest, bundlefile):
    """update the sample with submission alias adding a new sample"""
    # print('adding sample to bundle sample xml')
    tree = ElementTree.parse(bundlefile)
    root = tree.getroot()
    sample_count = 0
    for sample in manifest.samples:
        if sample.taxonomy_id == 32644:
            continue
        sample_count += 1
        sample_alias = ElementTree.SubElement(root, 'SAMPLE')
        sample_alias.set('alias', str(sample.sample_id))
        sample_alias.set('center_name', 'SangerInstitute')
        title = str(sample.sample_id) + '-tol'

        title_block = ElementTree.SubElement(sample_alias, 'TITLE')
        title_block.text = title
        sample_name = ElementTree.SubElement(sample_alias, 'SAMPLE_NAME')
        taxon_id = ElementTree.SubElement(sample_name, 'TAXON_ID')
        taxon_id.text = str(sample.taxonomy_id)
        sample_attributes = ElementTree.SubElement(sample_alias, 'SAMPLE_ATTRIBUTES')

        ena_fields = sample.to_ena_dict()
        for item in ena_fields:
            sample_attribute = ElementTree.SubElement(sample_attributes, 'SAMPLE_ATTRIBUTE')
            tag = ElementTree.SubElement(sample_attribute, 'TAG')
            tag.text = item
            value = ElementTree.SubElement(sample_attribute, 'VALUE')
            value.text = str(ena_fields[item]['value'])
            # add ena units where necessary
            if 'units' in ena_fields[item]:
                unit = ElementTree.SubElement(sample_attribute, 'UNITS')
                unit.text = ena_fields[item]['units']

    ElementTree.dump(tree)
    tree.write(open(bundlefile, 'w'),
               encoding='unicode')
    return sample_count


def build_submission_xml(manifest):
    # build submission XML
    tree = ElementTree.parse('main/templates/submission.xml')
    root = tree.getroot()
    # set submission attributes
    # root.set('submission_date', datetime.utcnow()
    #   .replace(tzinfo=d_utils.simple_utc()).isoformat())

    # set SRA contacts
    contacts = root.find('CONTACTS')

    # set copo sra contacts
    copo_contact = ElementTree.SubElement(contacts, 'CONTACT')
    copo_contact.set('name', os.getenv('ENA_CONTACT_NAME'))
    copo_contact.set('inform_on_error', os.getenv('ENA_CONTACT_EMAIL'))
    copo_contact.set('inform_on_status', os.getenv('ENA_CONTACT_EMAIL'))
    ElementTree.dump(tree)
    dir_ = tempfile.TemporaryDirectory()

    submissionfile = dir_.name + 'submission_' + str(manifest.manifest_id) + '.xml'

    tree.write(open(submissionfile, 'w'),
               encoding='unicode')

    return submissionfile
