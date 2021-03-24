from __future__ import absolute_import

from swagger_server.test import BaseTestCase

from swagger_server.manifest_utils import validate_manifest
from swagger_server.model import db, SubmissionsManifest, SubmissionsSample


class TestManifestUtils(BaseTestCase):

    def test_validate_manifest(self):
        self.manifest1 = SubmissionsManifest()
        self.sample1 = SubmissionsSample(collected_by="ALEX COLLECTOR",
                                         collection_location="UK | DARK FOREST",
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


if __name__ == '__main__':
    import unittest
    unittest.main()
