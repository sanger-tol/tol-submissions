from __future__ import absolute_import

from swagger_server.test import BaseTestCase

from swagger_server.manifest_utils import validate_manifest, validate_against_ena_checklist, \
    validate_ena_submittable, validate_against_tolid, generate_tolids_for_manifest, \
    generate_ena_ids_for_manifest, set_relationships_for_manifest
from swagger_server.model import db, SubmissionsManifest, SubmissionsSample, \
    SubmissionsSpecimen
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
        self.manifest1.project_name = "TestProj1"
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
        manifest = SubmissionsManifest()
        manifest.project_name = "MostExcellentProject"
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
        sample.manifest = manifest

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
        manifest = SubmissionsManifest()
        manifest.project_name = "MostExcellentProject"
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
        sample.manifest = manifest

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

    @responses.activate
    def test_generate_tolids_for_manifest(self):
        mock_response_from_tolid = [{
            "species": {
                "commonName": "lugworm",
                "family": "Arenicolidae",
                "genus": "Arenicola",
                "kingdom": "Metazoa",
                "order": "Capitellida",
                "phylum": "Annelida",
                "prefix": "wuAreMari",
                "scientificName": "Arenicola marina",
                "taxaClass": "Polychaeta",
                "taxonomyId": 6344
            },
            "specimen": {
                "specimenId": "specimen1234"
            },
            "tolId": "wuAreMari1"
        }]
        responses.add(responses.POST, os.environ['TOLID_URL'] + '/tol-ids',
                      json=mock_response_from_tolid, status=200)

        manifest = SubmissionsManifest()
        manifest.user = self.user1

        sample = SubmissionsSample()
        sample.row = 1
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
        sample.manifest = manifest

        sample2 = SubmissionsSample()
        sample2.row = 2
        sample2.specimen_id = "specimen1234"
        sample2.taxonomy_id = 6344
        sample2.scientific_name = "Arenicola marina"
        sample2.family = "Arenicolidae"
        sample2.genus = "Arenicola"
        sample2.order_or_group = "None"
        sample2.common_name = "lugworm"
        sample2.lifestage = "ADULT"
        sample2.sex = "FEMALE"
        sample2.organism_part = "THORAX"
        sample2.GAL = "Sanger Institute"
        sample2.GAL_sample_id = "SAN000100"
        sample2.collected_by = "ALEX COLLECTOR"
        sample2.collector_affiliation = "THE COLLECTOR INSTUTUTE"
        sample2.date_of_collection = "2020-09-01"
        sample2.collection_location = "UNITED KINGDOM | DARK FOREST"
        sample2.decimal_latitude = "+50.12345678"
        sample2.decimal_longitude = "-1.98765432"
        sample2.habitat = "WOODLAND"
        sample2.identified_by = "JO IDENTIFIER"
        sample2.identifier_affiliation = "THE IDENTIFIER INSTITUTE"
        sample2.voucher_id = "voucher1"
        sample2.elevation = "1500"
        sample2.depth = "1000"
        sample2.relationship = "child of 1234"
        sample2.manifest = manifest
        db.session.add(manifest)
        db.session.commit()

        number_of_errors, results = generate_tolids_for_manifest(manifest)

        self.assertEqual(0, number_of_errors)
        self.assertEqual([], results)
        self.assertEqual("wuAreMari1", sample.tolid)
        self.assertEqual("wuAreMari1", sample2.tolid)

    @responses.activate
    def test_generate_tolids_for_manifest_failure(self):
        mock_response_from_tolid = [{
            "species": {
                "commonName": "lugworm",
                "family": "Arenicolidae",
                "genus": "Arenicola",
                "kingdom": "Metazoa",
                "order": "Capitellida",
                "phylum": "Annelida",
                "prefix": "wuAreMari",
                "scientificName": "Arenicola marina",
                "taxaClass": "Polychaeta",
                "taxonomyId": 6344
            },
            "specimen": {
                "specimenId": "specimen1234"
            },
            "requestId": 1
        }]
        responses.add(responses.POST, os.environ['TOLID_URL'] + '/tol-ids',
                      json=mock_response_from_tolid, status=200)

        manifest = SubmissionsManifest()
        manifest.user = self.user1

        sample = SubmissionsSample()
        sample.row = 1
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
        sample.manifest = manifest

        sample2 = SubmissionsSample()
        sample2.row = 2
        sample2.specimen_id = "specimen1234"
        sample2.taxonomy_id = 6344
        sample2.scientific_name = "Arenicola marina"
        sample2.family = "Arenicolidae"
        sample2.genus = "Arenicola"
        sample2.order_or_group = "None"
        sample2.common_name = "lugworm"
        sample2.lifestage = "ADULT"
        sample2.sex = "FEMALE"
        sample2.organism_part = "THORAX"
        sample2.GAL = "Sanger Institute"
        sample2.GAL_sample_id = "SAN000100"
        sample2.collected_by = "ALEX COLLECTOR"
        sample2.collector_affiliation = "THE COLLECTOR INSTUTUTE"
        sample2.date_of_collection = "2020-09-01"
        sample2.collection_location = "UNITED KINGDOM | DARK FOREST"
        sample2.decimal_latitude = "+50.12345678"
        sample2.decimal_longitude = "-1.98765432"
        sample2.habitat = "WOODLAND"
        sample2.identified_by = "JO IDENTIFIER"
        sample2.identifier_affiliation = "THE IDENTIFIER INSTITUTE"
        sample2.voucher_id = "voucher1"
        sample2.elevation = "1500"
        sample2.depth = "1000"
        sample2.relationship = "child of 1234"
        sample2.manifest = manifest
        db.session.add(manifest)
        db.session.commit()

        expected = [{"row": 1,
                     "results": [{"field": "TAXON_ID",
                                  "message": "A ToLID has not been generated"}]},
                    {"row": 2,
                     "results": [{"field": "TAXON_ID",
                                  "message": "A ToLID has not been generated"}]}]

        number_of_errors, results = generate_tolids_for_manifest(manifest)

        self.assertEqual(2, number_of_errors)
        self.assertEqual(expected, results)
        self.assertEqual(None, sample.tolid)
        self.assertEqual(None, sample2.tolid)

    def test_set_relationships_for_manifest_existing_specimen(self):
        manifest = SubmissionsManifest()
        manifest.user = self.user1

        sample = SubmissionsSample()
        sample.row = 1
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
        sample.manifest = manifest

        specimen = SubmissionsSpecimen()
        specimen.specimen_id = "specimen1234"
        specimen.biosample_id = "SAMEA12345678"
        db.session.add(specimen)
        db.session.commit()

        error_count, results = set_relationships_for_manifest(manifest)
        self.assertEqual("SAMEA12345678", manifest.samples[0].sample_derived_from)
        self.assertEqual(None, manifest.samples[0].sample_same_as)
        self.assertEqual(None, manifest.samples[0].sample_symbiont_of)
        self.assertEqual(0, error_count)
        self.assertEqual([], results)

    @responses.activate
    def test_set_relationships_for_manifest_new_specimen(self):
        manifest = SubmissionsManifest()
        manifest.user = self.user1

        sample = SubmissionsSample()
        sample.row = 1
        sample.specimen_id = "specimen1234"
        sample.taxonomy_id = 6344
        sample.scientific_name = "Arenicola marina"
        sample.family = "Arenicolidae"
        sample.genus = "Arenicola"
        sample.order_or_group = "None"
        sample.common_name = "lugworm"
        sample.lifestage = "ADULT"
        sample.sex = "FEMALE"
        sample.organism_part = "WHOLE_ORGANISM"
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
        sample.manifest = manifest

        mock_response_from_ena = '<?xml version="1.0" encoding="UTF-8"?><?xml-stylesheet type="text/xsl" href="receipt.xsl"?><RECEIPT receiptDate="2021-04-07T12:47:39.998+01:00" submissionFile="tmphz9luulrsubmission_3.xml" success="true"><SAMPLE accession="ERS6206028" alias="' + str(1) + '" status="PRIVATE"><EXT_ID accession="SAMEA8521239" type="biosample"/></SAMPLE><SUBMISSION accession="ERA3819349" alias="SUBMISSION-07-04-2021-12:47:36:825"/><ACTIONS>ADD</ACTIONS></RECEIPT>'  # noqa
        responses.add(responses.POST, os.environ['ENA_URL'] + '/ena/submit/drop-box/submit/',
                      body=mock_response_from_ena, status=200)

        error_count, results = set_relationships_for_manifest(manifest)
        self.assertEqual(None, manifest.samples[0].sample_derived_from)
        self.assertEqual("SAMEA8521239", manifest.samples[0].sample_same_as)
        self.assertEqual(None, manifest.samples[0].sample_symbiont_of)
        self.assertEqual(0, error_count)
        self.assertEqual([], results)

        # Check the new specimen manifest
        specimen_manifest = db.session.query(SubmissionsManifest) \
            .filter(SubmissionsManifest.manifest_id == 1) \
            .one_or_none()

        self.assertEqual("SAMEA8521239", specimen_manifest.samples[0].biosample_id)

        # Check the new specimen
        specimen = db.session.query(SubmissionsSpecimen) \
            .filter(SubmissionsSpecimen.specimen_id == "specimen1234") \
            .one_or_none()

        self.assertEqual("SAMEA8521239", specimen.biosample_id)

    @responses.activate
    def test_set_relationships_for_manifest_new_specimen_ena_error(self):
        manifest = SubmissionsManifest()
        manifest.user = self.user1

        sample = SubmissionsSample()
        sample.row = 1
        sample.specimen_id = "specimen1234"
        sample.taxonomy_id = 6344
        sample.scientific_name = "Arenicola marina"
        sample.family = "Arenicolidae"
        sample.genus = "Arenicola"
        sample.order_or_group = "None"
        sample.common_name = "lugworm"
        sample.lifestage = "ADULT"
        sample.sex = "FEMALE"
        sample.organism_part = "WHOLE_ORGANISM"
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
        sample.manifest = manifest

        mock_response_from_ena = '<?xml version="1.0" encoding="UTF-8"?><?xml-stylesheet type="text/xsl" href="receipt.xsl"?><RECEIPT receiptDate="2021-04-07T12:47:39.998+01:00" submissionFile="tmphz9luulrsubmission_3.xml" success="true"><SAMPLE accession="ERS6206028" alias="' + str(1) + '" status="PRIVATE"><EXT_ID accession="SAMEA8521239" type="biosample"/></SAMPLE><SUBMISSION accession="ERA3819349" alias="SUBMISSION-07-04-2021-12:47:36:825"/><ACTIONS>ADD</ACTIONS></RECEIPT>'  # noqa
        responses.add(responses.POST, os.environ['ENA_URL'] + '/ena/submit/drop-box/submit/',
                      body=mock_response_from_ena, status=403)

        error_count, results = set_relationships_for_manifest(manifest)
        self.assertEqual(None, manifest.samples[0].sample_derived_from)
        self.assertEqual(None, manifest.samples[0].sample_same_as)
        self.assertEqual(None, manifest.samples[0].sample_symbiont_of)
        self.assertEqual(1, error_count)
        self.assertEqual([{'results': [{'field': 'TAXON_ID',
                                        'message': 'Cannot connect to ENA service'}],
                           'row': 1}], results)

    @responses.activate
    def test_generate_ena_ids_for_manifest(self):
        manifest = SubmissionsManifest()
        manifest.user = self.user1

        sample = SubmissionsSample()
        sample.row = 1
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
        sample.manifest = manifest

        sample2 = SubmissionsSample()
        sample2.row = 2
        sample2.specimen_id = "specimen1234"
        sample2.taxonomy_id = 6344
        sample2.scientific_name = "Arenicola marina"
        sample2.family = "Arenicolidae"
        sample2.genus = "Arenicola"
        sample2.order_or_group = "None"
        sample2.common_name = "lugworm"
        sample2.lifestage = "ADULT"
        sample2.sex = "FEMALE"
        sample2.organism_part = "THORAX"
        sample2.GAL = "Sanger Institute"
        sample2.GAL_sample_id = "SAN000100"
        sample2.collected_by = "ALEX COLLECTOR"
        sample2.collector_affiliation = "THE COLLECTOR INSTUTUTE"
        sample2.date_of_collection = "2020-09-01"
        sample2.collection_location = "UNITED KINGDOM | DARK FOREST"
        sample2.decimal_latitude = "+50.12345678"
        sample2.decimal_longitude = "-1.98765432"
        sample2.habitat = "WOODLAND"
        sample2.identified_by = "JO IDENTIFIER"
        sample2.identifier_affiliation = "THE IDENTIFIER INSTITUTE"
        sample2.voucher_id = "voucher1"
        sample2.elevation = "1500"
        sample2.depth = "1000"
        sample2.relationship = "child of 1234"
        sample2.manifest = manifest
        db.session.add(manifest)
        db.session.commit()

        mock_response_from_ena = '<?xml version="1.0" encoding="UTF-8"?><?xml-stylesheet type="text/xsl" href="receipt.xsl"?><RECEIPT receiptDate="2021-04-07T12:47:39.998+01:00" submissionFile="tmphz9luulrsubmission_3.xml" success="true"><SAMPLE accession="ERS6206028" alias="' + str(sample.sample_id) + '" status="PRIVATE"><EXT_ID accession="SAMEA8521239" type="biosample"/></SAMPLE><SAMPLE accession="ERS6206028B" alias="' + str(sample2.sample_id) + '" status="PRIVATE"><EXT_ID accession="SAMEA8521239B" type="biosample"/></SAMPLE><SUBMISSION accession="ERA3819349" alias="SUBMISSION-07-04-2021-12:47:36:825"/><ACTIONS>ADD</ACTIONS></RECEIPT>'  # noqa
        responses.add(responses.POST, os.environ['ENA_URL'] + '/ena/submit/drop-box/submit/',
                      body=mock_response_from_ena, status=200)

        number_of_errors, results = generate_ena_ids_for_manifest(manifest)

        self.assertEqual(0, number_of_errors)
        self.assertEqual([], results)
        self.assertEqual("SAMEA8521239", sample.biosample_id)
        self.assertEqual("ERS6206028", sample.sra_accession)
        self.assertEqual("ERA3819349", sample.submission_accession)
        self.assertEqual("SAMEA8521239B", sample2.biosample_id)
        self.assertEqual("ERS6206028B", sample2.sra_accession)
        self.assertEqual("ERA3819349", sample2.submission_accession)
        self.assertEqual(True, manifest.submission_status)
        self.assertTrue(sample.submission_error is None)
        self.assertTrue(sample.submission_error is None)

    @responses.activate
    def test_generate_ena_ids_for_manifest_connection_failed(self):
        manifest = SubmissionsManifest()
        manifest.user = self.user1

        sample = SubmissionsSample()
        sample.row = 1
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
        sample.manifest = manifest

        db.session.add(manifest)
        db.session.commit()

        mock_response_from_ena = ''  # noqa
        responses.add(responses.POST, os.environ['ENA_URL'] + '/ena/submit/drop-box/submit/',
                      body=mock_response_from_ena, status=404)

        number_of_errors, results = generate_ena_ids_for_manifest(manifest)

        expected = [{'results': [{'field': 'TAXON_ID',
                                  'message': 'Cannot connect to ENA service'}],
                     'row': 1}]
        self.assertEqual(1, number_of_errors)
        self.assertEqual(expected, results)

        self.assertEqual(None, sample.biosample_id)
        self.assertEqual(None, sample.sra_accession)
        self.assertEqual(None, sample.submission_accession)
        self.assertEqual(None, manifest.submission_status)
        self.assertTrue(sample.submission_error is None)

    @responses.activate
    def test_generate_ena_ids_for_manifest_already_exist(self):
        manifest = SubmissionsManifest()
        manifest.user = self.user1

        sample = SubmissionsSample()
        sample.row = 1
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
        sample.manifest = manifest

        db.session.add(manifest)
        db.session.commit()

        mock_response_from_ena = '<?xml version="1.0" encoding="UTF-8"?><?xml-stylesheet type="text/xsl" href="receipt.xsl"?><RECEIPT receiptDate="2021-04-07T15:48:38.322+01:00" submissionFile="tmpqj34wkifsubmission_2.xml" success="false"><SAMPLE alias="' + str(manifest.samples[0].sample_id) + '" status="PRIVATE"/><SUBMISSION alias="SUBMISSION-07-04-2021-15:48:38:302"/><MESSAGES><ERROR>In sample, alias:"' + str(manifest.samples[0].sample_id) + '", accession:"". The object being added already exists in the submission account with accession: "ERS6206044".</ERROR></MESSAGES><ACTIONS>ADD</ACTIONS></RECEIPT>'  # noqa
        responses.add(responses.POST, os.environ['ENA_URL'] + '/ena/submit/drop-box/submit/',
                      body=mock_response_from_ena, status=200)

        number_of_errors, results = generate_ena_ids_for_manifest(manifest)

        expected = [{'results': [{'field': 'TAXON_ID',
                                  'message': 'Error returned from ENA service'}],
                     'row': 1}]
        self.assertEqual(1, number_of_errors)
        self.assertEqual(expected, results)
        self.assertEqual(None, sample.biosample_id)
        self.assertEqual(None, sample.sra_accession)
        self.assertEqual(None, sample.submission_accession)
        self.assertEqual(False, manifest.submission_status)
        self.assertTrue(sample.submission_error is not None)


if __name__ == '__main__':
    import unittest
    unittest.main()
