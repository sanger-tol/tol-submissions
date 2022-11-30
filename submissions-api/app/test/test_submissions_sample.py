# SPDX-FileCopyrightText: 2021 Genome Research Ltd.
#
# SPDX-License-Identifier: MIT

from __future__ import absolute_import

from test import BaseTestCase

from main.model import SubmissionsManifest, SubmissionsSample


class TestSubmissionsSample(BaseTestCase):

    def test_country_region(self):
        sample = SubmissionsSample()

        # Correct
        sample.collection_location = 'United Kingdom | England | Cambridge'
        self.assertEqual(sample.collection_country(), 'United Kingdom')
        self.assertEqual(sample.collection_region(), 'England | Cambridge')

        # No space near delimiter
        sample.collection_location = 'United Kingdom| England |Cambridge'
        self.assertEqual(sample.collection_country(), 'United Kingdom')
        self.assertEqual(sample.collection_region(), 'England | Cambridge')

        # Only country
        sample.collection_location = 'United Kingdom'
        self.assertEqual(sample.collection_country(), 'United Kingdom')
        self.assertEqual(sample.collection_region(), '')

        # Blank
        sample.collection_location = ''
        self.assertEqual(sample.collection_country(), '')
        self.assertEqual(sample.collection_region(), '')

    def test_ena_dict(self):
        manifest = SubmissionsManifest()
        manifest.user = self.user1
        manifest.project_name = 'AwesomeProject'
        sample = SubmissionsSample()
        sample.specimen_id = 'specimen1234'
        sample.taxonomy_id = 6344
        sample.scientific_name = 'Arenicola marina2'
        sample.family = 'Arenicolidae2'
        sample.genus = 'Arenicola2'
        sample.order_or_group = 'None2'
        sample.common_name = 'lugworm'
        sample.lifestage = 'ADULT'
        sample.sex = 'FEMALE'
        sample.organism_part = 'MUSCLE'
        sample.GAL = 'Sanger Institute'
        sample.GAL_sample_id = 'SAN000100'
        sample.collected_by = 'ALEX COLLECTOR'
        sample.collector_affiliation = 'THE COLLECTOR INSTUTUTE'
        sample.date_of_collection = '2020-09-01'
        sample.collection_location = 'UNITED KINGDOM | DARK FOREST'
        sample.decimal_latitude = '+50.12345678'
        sample.decimal_longitude = '-1.98765432'
        sample.habitat = 'WOODLAND'
        sample.identified_by = 'JO IDENTIFIER'
        sample.identifier_affiliation = 'THE IDENTIFIER INSTITUTE'
        sample.voucher_id = 'voucher1'
        sample.elevation = '1500'
        sample.depth = '1000'
        sample.relationship = 'child of 1234'
        sample.manifest = manifest

        expected = {'ENA-CHECKLIST': {'value': 'ERC000053'},
                    'organism part': {'value': 'MUSCLE'},
                    'lifestage': {'value': 'ADULT'},
                    'project name': {'value': 'AwesomeProject'},
                    'tolid': {'value': None},
                    'collected by': {'value': 'ALEX COLLECTOR'},
                    'collection date': {'value': '2020-09-01'},
                    'geographic location (country and/or sea)': {'value': 'UNITED KINGDOM'},
                    'geographic location (latitude)': {'units': 'DD', 'value': '+50.12345678'},
                    'geographic location (longitude)': {'units': 'DD', 'value': '-1.98765432'},
                    'geographic location (region and locality)': {'value': 'DARK FOREST'},
                    'identified_by': {'value': 'JO IDENTIFIER'},
                    'geographic location (depth)': {'units': 'm', 'value': '1000'},
                    'geographic location (elevation)': {'units': 'm', 'value': '1500'},
                    'habitat': {'value': 'WOODLAND'},
                    'identifier_affiliation': {'value': 'THE IDENTIFIER INSTITUTE'},
                    'sex': {'value': 'FEMALE'},
                    'relationship': {'value': 'child of 1234'},
                    'collecting institution': {'value': 'THE COLLECTOR INSTUTUTE'},
                    'GAL': {'value': 'Sanger Institute'},
                    'specimen_voucher': {'value': 'voucher1'},
                    'specimen_id': {'value': 'specimen1234'},
                    'GAL_sample_id': {'value': 'SAN000100'}}
        self.assertEqual(sample.to_ena_dict(), expected)

    def test_is_symbiont(self):
        sample = SubmissionsSample()
        sample.symbiont = None
        self.assertFalse(sample.is_symbiont())
        sample.symbiont = 'TARGET'
        self.assertFalse(sample.is_symbiont())
        sample.symbiont = 'SYMBIONT'
        self.assertTrue(sample.is_symbiont())


if __name__ == '__main__':
    import unittest
    unittest.main()
