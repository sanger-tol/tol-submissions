from __future__ import absolute_import

from swagger_server.test import BaseTestCase

from swagger_server.manifest_utils import validate_manifest, validate_against_ena_checklist, \
    validate_ena_submittable, validate_against_tolid
from swagger_server.model import db, SubmissionsManifest, SubmissionsSample
import os
import responses


class TestManifestUtils(BaseTestCase):

    @responses.activate
    def test_validate_manifest(self):
        mock_response_from_ena = {"taxId": "6344",
                                  "scientificName": "Arenicola marina",
                                  "commonName": "lugworm",
                                  "formalName": "true",
                                  "rank": "species",
                                  "division": "INV",
                                  "lineage": "",
                                  "geneticCode": "1",
                                  "mitochondrialGeneticCode": "5",
                                  "submittable": "true"}
        responses.add(responses.GET, 'https://www.ebi.ac.uk/ena/taxonomy/rest/tax-id/6344',
                      json=mock_response_from_ena, status=200)
        mock_response_from_tolid = [{"taxonomyId": "6344",
                                     "scientificName": "Arenicola marina",
                                     "commonName": "lugworm",
                                     "family": "Arenicolidae",
                                     "genus": "Arenicola",
                                     "order": "None"}]
        responses.add(responses.GET, os.environ['TOLID_URL'] + '/species/6344',
                      json=mock_response_from_tolid, status=200)

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
                                         family="Arenicolidae",
                                         GAL="SANGER INSTITUTE",
                                         GAL_sample_id="SAN000100",
                                         genus="Arenicola",
                                         habitat="Woodland",
                                         identified_by="JO IDENTIFIER",
                                         identifier_affiliation="THE IDENTIFIER INSTITUTE",
                                         lifestage="ADULT",
                                         organism_part="MUSCLE",
                                         order_or_group="None",
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
        self.sample1.organism_part = ""
        number_of_errors, results = validate_manifest(self.manifest1)
        self.assertEqual(number_of_errors, 1)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]["results"]), 1)

    def test_validate_against_ena_checklist_fail(self):
        sample = SubmissionsSample()
        sample.specimen_id = ""
        sample.taxonomy_id = ""
        sample.scientific_name = ""
        sample.family = ""
        sample.genus = ""
        sample.order_or_group = ""
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
        sample.decimal_longitude = "Greenwich meridian"
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
                     'message': 'Must be in allowed values'},
                    {'field': 'COLLECTED_BY', 'message': 'Must not be empty'},
                    {'field': 'DATE_OF_COLLECTION', 'message': 'Must match specific pattern'},
                    {'field': 'COLLECTION_LOCATION', 'message': 'Must be in allowed values'},
                    {'field': 'DECIMAL_LATITUDE', 'message': 'Must not be empty'},
                    {'field': 'DECIMAL_LONGITUDE', 'message': 'Must match specific pattern'},
                    {'field': 'IDENTIFIED_BY', 'message': 'Must not be empty'},
                    {'field': 'DEPTH', 'message': 'Must match specific pattern'},
                    {'field': 'ELEVATION', 'message': 'Must match specific pattern'},
                    {'field': 'HABITAT', 'message': 'Must not be empty'},
                    {'field': 'IDENTIFIER_AFFILIATION', 'message': 'Must not be empty'},
                    {'field': 'SEX', 'message': 'Must not be empty'},
                    {'field': 'COLLECTOR_AFFILIATION', 'message': 'Must not be empty'},
                    {'field': 'GAL', 'message': 'Must be in allowed values'},
                    {'field': 'VOUCHER_ID', 'message': 'Must not be empty'},
                    {'field': 'SPECIMEN_ID', 'message': 'Must not be empty'},
                    {'field': 'GAL_SAMPLE_ID', 'message': 'Must not be empty'}]

        self.assertEqual(results, expected)

    def test_validate_against_ena_checklist_pass(self):
        sample = SubmissionsSample()
        sample.specimen_id = "specimen1234"
        sample.taxonomy_id = 6344
        sample.scientific_name = "Arenicola marina"
        sample.family = "Arenicolidae"
        sample.genus = "Arenicola"
        sample.order_or_group = "None"
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

    # The real version of this does a call to the ENA service. We mock that call here
    @responses.activate
    def test_validate_ena_submittable_correct(self):
        mock_response_from_ena = {"taxId": "6344",
                                  "scientificName": "Arenicola marina",
                                  "commonName": "lugworm",
                                  "formalName": "true",
                                  "rank": "species",
                                  "division": "INV",
                                  "lineage": "",
                                  "geneticCode": "1",
                                  "mitochondrialGeneticCode": "5",
                                  "submittable": "true"}
        responses.add(responses.GET, 'https://www.ebi.ac.uk/ena/taxonomy/rest/tax-id/6344',
                      json=mock_response_from_ena, status=200)

        sample = SubmissionsSample()
        sample.specimen_id = "specimen1234"
        sample.taxonomy_id = 6344
        sample.scientific_name = "Arenicola marina"
        sample.family = "Arenicolidae"
        sample.genus = "Arenicola"
        sample.order_or_group = "None"
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

        results = validate_ena_submittable(sample)
        expected = []

        self.assertEqual(results, expected)

    @responses.activate
    def test_validate_ena_submittable_fail(self):
        mock_response_from_ena = {"taxId": "6344",
                                  "scientificName": "Arenicola marina2",
                                  "commonName": "lugworm",
                                  "formalName": "true",
                                  "rank": "species",
                                  "division": "INV",
                                  "lineage": "",
                                  "geneticCode": "1",
                                  "mitochondrialGeneticCode": "5",
                                  "submittable": "false"}
        responses.add(responses.GET, 'https://www.ebi.ac.uk/ena/taxonomy/rest/tax-id/6344',
                      json=mock_response_from_ena, status=200)

        sample = SubmissionsSample()
        sample.specimen_id = "specimen1234"
        sample.taxonomy_id = 6344
        sample.scientific_name = "Arenicola marina"
        sample.family = "Arenicolidae"
        sample.genus = "Arenicola"
        sample.order_or_group = "None"
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

        results = validate_ena_submittable(sample)
        expected = [{"field": "TAXON_ID",
                     "message": "Is not ENA submittable"},
                    {'field': 'SCIENTIFIC_NAME',
                     'message': 'Must match ENA (expected Arenicola marina2)'}]

        self.assertEqual(results, expected)

    @responses.activate
    def test_validate_ena_submittable_not_found(self):
        mock_response_from_ena = "No results."
        responses.add(responses.GET, 'https://www.ebi.ac.uk/ena/taxonomy/rest/tax-id/6344',
                      body=mock_response_from_ena, status=200)

        sample = SubmissionsSample()
        sample.specimen_id = "specimen1234"
        sample.taxonomy_id = 6344
        sample.scientific_name = "Arenicola marina"
        sample.family = "Arenicolidae"
        sample.genus = "Arenicola"
        sample.order_or_group = "None"
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

        results = validate_ena_submittable(sample)
        expected = [{"field": "TAXON_ID",
                     "message": "Is not known at ENA"}]

        self.assertEqual(results, expected)

    @responses.activate
    def test_validate_ena_submittable_cannot_connect(self):
        mock_response_from_ena = "No results."
        responses.add(responses.GET, 'https://www.ebi.ac.uk/ena/taxonomy/rest/tax-id/6344',
                      body=mock_response_from_ena, status=500)

        sample = SubmissionsSample()
        sample.specimen_id = "specimen1234"
        sample.taxonomy_id = 6344
        sample.scientific_name = "Arenicola marina"
        sample.family = "Arenicolidae"
        sample.genus = "Arenicola"
        sample.order_or_group = "None"
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

        results = validate_ena_submittable(sample)
        expected = [{"field": "TAXON_ID",
                     "message": "Communication with ENA has failed with status code 500"}]

        self.assertEqual(results, expected)

    # The real version of this does a call to the ToLID service. We mock that call here
    @responses.activate
    def test_validate_tolid_correct(self):
        mock_response_from_tolid = [{"taxonomyId": "6344",
                                     "scientificName": "Arenicola marina",
                                     "commonName": "lugworm",
                                     "family": "Arenicolidae",
                                     "genus": "Arenicola",
                                     "order": "None"}]
        responses.add(responses.GET, os.environ['TOLID_URL'] + '/species/6344',
                      json=mock_response_from_tolid, status=200)

        sample = SubmissionsSample()
        sample.specimen_id = "specimen1234"
        sample.taxonomy_id = 6344
        sample.scientific_name = "Arenicola marina"
        sample.family = "Arenicolidae"
        sample.genus = "Arenicola"
        sample.order_or_group = "None"
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

        results = validate_against_tolid(sample)
        expected = []

        self.assertEqual(results, expected)

    # The real version of this does a call to the ToLID service. We mock that call here
    @responses.activate
    def test_validate_tolid_species_missing(self):
        mock_response_from_tolid = []
        responses.add(responses.GET, os.environ['TOLID_URL'] + '/species/6344',
                      json=mock_response_from_tolid, status=404)

        sample = SubmissionsSample()
        sample.specimen_id = "specimen1234"
        sample.taxonomy_id = 6344
        sample.scientific_name = "Arenicola marina"
        sample.family = "Arenicolidae"
        sample.genus = "Arenicola"
        sample.order_or_group = "None"
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

        results = validate_against_tolid(sample)
        expected = [{"field": "TAXON_ID",
                     "message": "Species not known in the ToLID service"}]

        self.assertEqual(results, expected)

    # The real version of this does a call to the ToLID service. We mock that call here
    @responses.activate
    def test_validate_tolid_cant_communicate(self):
        mock_response_from_tolid = []
        responses.add(responses.GET, os.environ['TOLID_URL'] + '/species/6344',
                      json=mock_response_from_tolid, status=500)

        sample = SubmissionsSample()
        sample.specimen_id = "specimen1234"
        sample.taxonomy_id = 6344
        sample.scientific_name = "Arenicola marina"
        sample.family = "Arenicolidae"
        sample.genus = "Arenicola"
        sample.order_or_group = "None"
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

        results = validate_against_tolid(sample)
        expected = [{"field": "TAXON_ID",
                     "message": "Communication failed with the ToLID service: status code 500"}]

        self.assertEqual(results, expected)

    # The real version of this does a call to the ToLID service. We mock that call here
    @responses.activate
    def test_validate_tolid_name_genus_family_order(self):
        mock_response_from_tolid = [{"taxonomyId": "6344",
                                     "scientificName": "Arenicola marina",
                                     "commonName": "lugworm",
                                     "family": "Arenicolidae",
                                     "genus": "Arenicola",
                                     "order": "None"}]
        responses.add(responses.GET, os.environ['TOLID_URL'] + '/species/6344',
                      json=mock_response_from_tolid, status=200)

        sample = SubmissionsSample()
        sample.specimen_id = "specimen1234"
        sample.taxonomy_id = 6344
        sample.scientific_name = "Arenicola marina2"
        sample.family = "Arenicolidae2"
        sample.genus = "Arenicola2"
        sample.order_or_group = "None2"
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

        results = validate_against_tolid(sample)
        expected = [{"field": "SCIENTIFIC_NAME",
                     "message": "Does not match that in the ToLID service "
                     + "(expecting Arenicola marina)"},
                    {"field": "GENUS",
                     "message": "Does not match that in the ToLID service (expecting Arenicola)"},
                    {"field": "FAMILY",
                     "message": "Does not match that in the ToLID service "
                     + "(expecting Arenicolidae)"},
                    {"field": "ORDER_OR_GROUP",
                     "message": "Does not match that in the ToLID service (expecting None)"}]

        self.assertEqual(results, expected)


if __name__ == '__main__':
    import unittest
    unittest.main()
