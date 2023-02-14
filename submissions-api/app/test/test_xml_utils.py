# SPDX-FileCopyrightText: 2021 Genome Research Ltd.
#
# SPDX-License-Identifier: MIT

from __future__ import absolute_import

import os
from test import BaseTestCase

from main.model import SubmissionsManifest, SubmissionsSample, db
from main.xml_utils import build_bundle_sample_xml, build_submission_xml


class TestXmlUtils(BaseTestCase):

    def test_bundle_xml(self):

        manifest = SubmissionsManifest()
        sample = SubmissionsSample(collected_by='ALEX COLLECTOR',
                                   collection_location='UNITED KINGDOM | DARK FOREST',
                                   collector_affiliation='THE COLLECTOR INSTITUTE',
                                   common_name='lugworm',
                                   date_of_collection='2020-09-01',
                                   decimal_latitude='50.12345678',
                                   decimal_longitude='-1.98765432',
                                   depth='100',
                                   elevation='0',
                                   family='Arenicolidae',
                                   GAL='SANGER INSTITUTE',
                                   GAL_sample_id='SAN000100',
                                   genus='Arenicola',
                                   habitat='Woodland',
                                   identified_by='JO IDENTIFIER',
                                   identifier_affiliation='THE IDENTIFIER INSTITUTE',
                                   lifestage='ADULT',
                                   organism_part='MUSCLE',
                                   order_or_group='None',
                                   relationship='child of SAMEA1234567',
                                   scientific_name='Arenicola marina',
                                   sex='FEMALE',
                                   specimen_id='SAN000100',
                                   taxonomy_id=6344,
                                   voucher_id='voucher1',
                                   row=1)
        sample.manifest = manifest
        db.session.add(manifest)
        db.session.commit()
        filename, sample_count = build_bundle_sample_xml(manifest)
        f = open(filename, 'r')
        file_contents = f.read()
        f.close()
        expected = '<SAMPLE_SET xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="ftp://ftp.sra.ebi.ac.uk/meta/xsd/sra_1_5/SRA.sample.xsd"><SAMPLE alias="1" center_name="SangerInstitute"><TITLE>1-tol</TITLE><SAMPLE_NAME><TAXON_ID>6344</TAXON_ID></SAMPLE_NAME><SAMPLE_ATTRIBUTES><SAMPLE_ATTRIBUTE><TAG>ENA-CHECKLIST</TAG><VALUE>ERC000053</VALUE></SAMPLE_ATTRIBUTE><SAMPLE_ATTRIBUTE><TAG>organism part</TAG><VALUE>MUSCLE</VALUE></SAMPLE_ATTRIBUTE><SAMPLE_ATTRIBUTE><TAG>lifestage</TAG><VALUE>ADULT</VALUE></SAMPLE_ATTRIBUTE><SAMPLE_ATTRIBUTE><TAG>project name</TAG><VALUE>ToL</VALUE></SAMPLE_ATTRIBUTE><SAMPLE_ATTRIBUTE><TAG>tolid</TAG><VALUE>None</VALUE></SAMPLE_ATTRIBUTE><SAMPLE_ATTRIBUTE><TAG>collected by</TAG><VALUE>ALEX COLLECTOR</VALUE></SAMPLE_ATTRIBUTE><SAMPLE_ATTRIBUTE><TAG>collection date</TAG><VALUE>2020-09-01</VALUE></SAMPLE_ATTRIBUTE><SAMPLE_ATTRIBUTE><TAG>geographic location (country and/or sea)</TAG><VALUE>UNITED KINGDOM</VALUE></SAMPLE_ATTRIBUTE><SAMPLE_ATTRIBUTE><TAG>geographic location (latitude)</TAG><VALUE>50.12345678</VALUE><UNITS>DD</UNITS></SAMPLE_ATTRIBUTE><SAMPLE_ATTRIBUTE><TAG>geographic location (longitude)</TAG><VALUE>-1.98765432</VALUE><UNITS>DD</UNITS></SAMPLE_ATTRIBUTE><SAMPLE_ATTRIBUTE><TAG>geographic location (region and locality)</TAG><VALUE>DARK FOREST</VALUE></SAMPLE_ATTRIBUTE><SAMPLE_ATTRIBUTE><TAG>identified_by</TAG><VALUE>JO IDENTIFIER</VALUE></SAMPLE_ATTRIBUTE><SAMPLE_ATTRIBUTE><TAG>geographic location (depth)</TAG><VALUE>100</VALUE><UNITS>m</UNITS></SAMPLE_ATTRIBUTE><SAMPLE_ATTRIBUTE><TAG>geographic location (elevation)</TAG><VALUE>0</VALUE><UNITS>m</UNITS></SAMPLE_ATTRIBUTE><SAMPLE_ATTRIBUTE><TAG>habitat</TAG><VALUE>Woodland</VALUE></SAMPLE_ATTRIBUTE><SAMPLE_ATTRIBUTE><TAG>identifier_affiliation</TAG><VALUE>THE IDENTIFIER INSTITUTE</VALUE></SAMPLE_ATTRIBUTE><SAMPLE_ATTRIBUTE><TAG>sex</TAG><VALUE>FEMALE</VALUE></SAMPLE_ATTRIBUTE><SAMPLE_ATTRIBUTE><TAG>relationship</TAG><VALUE>child of SAMEA1234567</VALUE></SAMPLE_ATTRIBUTE><SAMPLE_ATTRIBUTE><TAG>collecting institution</TAG><VALUE>THE COLLECTOR INSTITUTE</VALUE></SAMPLE_ATTRIBUTE><SAMPLE_ATTRIBUTE><TAG>GAL</TAG><VALUE>SANGER INSTITUTE</VALUE></SAMPLE_ATTRIBUTE><SAMPLE_ATTRIBUTE><TAG>specimen_voucher</TAG><VALUE>voucher1</VALUE></SAMPLE_ATTRIBUTE><SAMPLE_ATTRIBUTE><TAG>specimen_id</TAG><VALUE>SAN000100</VALUE></SAMPLE_ATTRIBUTE><SAMPLE_ATTRIBUTE><TAG>GAL_sample_id</TAG><VALUE>SAN000100</VALUE></SAMPLE_ATTRIBUTE></SAMPLE_ATTRIBUTES></SAMPLE></SAMPLE_SET>'  # noqa
        self.assertEqual(file_contents.replace('\n', ''), expected)

    def test_submission_xml(self):
        manifest = SubmissionsManifest()
        db.session.add(manifest)
        db.session.commit()
        filename = build_submission_xml(manifest)
        f = open(filename, 'r')
        file_contents = f.read()
        f.close()
        expected = '<SUBMISSION xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="ftp://ftp.sra.ebi.ac.uk/meta/xsd/sra_1_5/SRA.submission.xsd"><CONTACTS><CONTACT name="' + os.getenv("ENA_CONTACT_NAME") + '" inform_on_error="' + os.getenv("ENA_CONTACT_EMAIL") + '" inform_on_status="' + os.getenv("ENA_CONTACT_EMAIL") + '" /></CONTACTS><ACTIONS><ACTION><ADD /></ACTION><ACTION><RELEASE /></ACTION></ACTIONS></SUBMISSION>'  # noqa
        self.assertEqual(
            file_contents.replace('\n', '').replace('&lt;', '<').replace('&gt;', '>'),
            expected
        )


if __name__ == '__main__':
    import unittest
    unittest.main()
