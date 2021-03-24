from __future__ import absolute_import

from swagger_server.test import BaseTestCase

from swagger_server.manifest_utils import validate_manifest, validate_against_ena_checklist
from swagger_server.model import db, SubmissionsManifest, SubmissionsSample


class TestManifestUtils(BaseTestCase):

    def test_validate_manifest(self):
        self.manifest1 = SubmissionsManifest()
        self.sample1 = SubmissionsSample(collected_by="ALEX COLLECTOR",
                                         collection_location="UNITED KINGDOM | DARK FOREST",
                                         collector_affiliation="THE COLLECTOR INSTITUTE",
                                         common_name="lugworm",
                                         date_of_collection="2020-09-01",
                                         decimal_latitude="50.12345678",
                                         decimal_longitude="-1.98765432",
                                         depth="100",
                                         elevation="0",
                                         GAL="SANGER INSTITUTE",
                                         GAL_sample_id="SAN000100",
                                         habitat="Woodland",
                                         identified_by="JO IDENTIFIER",
                                         identifier_affiliation="THE IDENTIFIER INSTITUTE",
                                         lifestage="ADULT",
                                         organism_part="MUSCLE",
                                         relationship="child of SAMEA1234567",
                                         scientific_name="Arenicola marina",
                                         sex="FEMALE",
                                         specimen_id="SAN000100",
                                         taxonomy_id=6344,
                                         voucher_id="voucher1",
                                         row=1)
        self.sample1.manifest = self.manifest1
        db.session.add(self.manifest1)
        db.session.add(self.sample1)

        number_of_errors, results = validate_manifest(self.manifest1)
        self.assertEqual(number_of_errors, 0)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]["results"]), 0)

        # Cause a validation failure
        self.sample1.scientific_name = ""
        number_of_errors, results = validate_manifest(self.manifest1)
        self.assertEqual(number_of_errors, 1)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]["results"]), 1)

    def test_validate_against_ena_checklist_fail(self):
        sample = SubmissionsSample()
        sample.specimen_id = ""
        sample.taxonomy_id = ""
        sample.scientific_name = ""
        sample.common_name = ""
        sample.lifestage = "random"
        sample.sex = ""
        sample.organism_part = ""
        sample.GAL = "Independent lab"
        sample.GAL_sample_id = ""
        sample.collected_by = ""
        sample.collector_affiliation = ""
        sample.date_of_collection = "1st May 2021"
        sample.collection_location = "Moon | Sea of Tranquility"
        sample.decimal_latitude = ""
        sample.decimal_longitude = ""
        sample.habitat = ""
        sample.identified_by = ""
        sample.identifier_affiliation = ""
        sample.voucher_id = ""
        sample.elevation = "quite high"
        sample.depth = "really low"
        sample.relationship = ""

        results = validate_against_ena_checklist(sample)
        expected = [{'field': 'ORGANISM_PART',
                     'message': 'Must not be empty'},
                    {'field': 'LIFESTAGE',
                     'message': 'Must be one of adult, egg, embryo, gametophyte, juvenile, '
                                + 'larva, not applicable, not collected, not provided, pupa, '
                                + 'spore-bearing structure, sporophyte, vegetative cell, '
                                + 'vegetative structure, zygote'},
                    {'field': 'COLLECTED_BY', 'message': 'Must not be empty'},
                    {'field': 'COLLECTION_DATE', 'message': 'Must match specific pattern'},
                    {'field': 'COLLECTION_LOCATION', 'message': 'Must be in the allowed list'},
                    {'field': 'DECIMAL_LATITUDE', 'message': 'Must match specific pattern'},
                    {'field': 'DECIMAL_LONGITUDE', 'message': 'Must match specific pattern'},
                    {'field': 'IDENTIFIED_BY', 'message': 'Must be given'},
                    {'field': 'HABITAT', 'message': 'Must be given'},
                    {'field': 'IDENTIFIER_AFFILIATION', 'message': 'Must be given'},
                    {'field': 'SEX', 'message': 'Must be given'},
                    {'field': 'COLLECTOR_AFFILIATION', 'message': 'Must be given'},
                    {'field': 'GAL', 'message': 'Must be in allowed list'},
                    {'field': 'VOUCHER_ID', 'message': 'Must be given'},
                    {'field': 'SPECIMEN_ID', 'message': 'Must be given'},
                    {'field': 'GAL_SAMPLE_ID', 'message': 'Must be given'},
                    {'field': 'DEPTH', 'message': 'Must match specific pattern'},
                    {'field': 'ELEVATION', 'message': 'Must match specific pattern'}]

        self.assertEqual(results, expected)

    def test_validate_against_ena_checklist_pass(self):
        sample = SubmissionsSample()
        sample.specimen_id = "specimen1234"
        sample.taxonomy_id = 9606
        sample.scientific_name = "Arenicola marina"
        sample.common_name = "lugworm"
        sample.lifestage = "ADULT"
        sample.sex = "FEMALE"
        sample.organism_part = "MUSCLE"
        sample.GAL = "Sanger Institute"
        sample.GAL_sample_id = "SAN000100"
        sample.collected_by = "ALEX COLLECTOR"
        sample.collector_affiliation = "THE COLLECTOR INSTUTUTE"
        sample.date_of_collection = "2020-09-01"
        sample.collection_location = "UNITED KINGDOM | DARK FOREST"
        sample.decimal_latitude = "+50.12345678"
        sample.decimal_longitude = "-1.98765432"
        sample.habitat = "WOODLAND"
        sample.identified_by = "JO IDENTIFIER"
        sample.identifier_affiliation = "THE IDENTIFIER INSTITUTE"
        sample.voucher_id = "voucher1"
        sample.elevation = "1500"
        sample.depth = "1000"
        sample.relationship = "child of 1234"

        results = validate_against_ena_checklist(sample)
        expected = []

        self.assertEqual(results, expected)


if __name__ == '__main__':
    import unittest
    unittest.main()
