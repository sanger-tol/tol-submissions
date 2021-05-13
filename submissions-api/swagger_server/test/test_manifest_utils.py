from __future__ import absolute_import

from swagger_server.test import BaseTestCase

from swagger_server.manifest_utils import validate_manifest, validate_against_ena_checklist, \
    validate_ena_submittable, validate_against_tolid, generate_tolids_for_manifest, \
    generate_ena_ids_for_manifest, set_relationships_for_manifest, validate_allowed_values, \
    validate_regexs, validate_specimen_id, validate_rack_plate_tube_well_not_both_na, \
    validate_rack_plate_tube_well_unique, validate_no_orphaned_symbionts, \
    validate_no_specimens_with_different_taxons, validate_barcoding, \
    validate_specimen_against_tolid, validate_sts_rack_plate_tube_well, \
    validate_whole_organisms_unique
from swagger_server.model import db, SubmissionsManifest, SubmissionsSample, \
    SubmissionsSpecimen
import os
import responses


class TestManifestUtils(BaseTestCase):

    def test_validate_allowed_values(self):
        self.sample1 = SubmissionsSample(collected_by="ALEX COLLECTOR",
                                         collection_location="UNITED KINGDOM | DARK FOREST",
                                         collector_affiliation="THE COLLECTOR INSTITUTE",
                                         common_name="lugworm",
                                         date_of_collection="2020-09-01",
                                         decimal_latitude="50.12345678",
                                         decimal_longitude="-1.98765432",
                                         depth="100",
                                         difficult_or_high_priority_sample="INVALID",
                                         elevation="0",
                                         family="Arenicolidae",
                                         GAL="SANGER INSTITUTE",
                                         GAL_sample_id="SAN000100",
                                         genus="Arenicola",
                                         habitat="Woodland",
                                         hazard_group="INVALID",
                                         identified_by="JO IDENTIFIER",
                                         identifier_affiliation="THE IDENTIFIER INSTITUTE",
                                         lifestage="ADULT",
                                         organism_part="INVALID",
                                         order_or_group="None",
                                         purpose_of_specimen="INVALID",
                                         regulatory_compliance="INVALID",
                                         relationship="child of SAMEA1234567",
                                         scientific_name="Arenicola marina",
                                         sex="INVALID",
                                         size_of_tissue_in_tube="INVALID",
                                         specimen_id="SAN000100",
                                         specimen_id_risk="INVALID",
                                         symbiont="INVALID",
                                         taxonomy_id=6344,
                                         tissue_for_barcoding="INVALID",
                                         tissue_removed_for_barcoding="INVALID",
                                         voucher_id="voucher1",
                                         row=1)
        expected = [{'field': 'SEX',
                     'message': 'Must be an allowed value',
                     'severity': 'ERROR'},
                    {'field': 'ORGANISM_PART',
                     'message': 'Must be an allowed value',
                     'severity': 'ERROR'},
                    {'field': 'SYMBIONT',
                     'message': 'Must be an allowed value',
                     'severity': 'ERROR'},
                    {'field': 'DIFFICULT_OR_HIGH_PRIORITY_SAMPLE',
                     'message': 'Must be an allowed value',
                     'severity': 'ERROR'},
                    {'field': 'SPECIMEN_ID_RISK',
                     'message': 'Must be an allowed value',
                     'severity': 'ERROR'},
                    {'field': 'SIZE_OF_TISSUE_IN_TUBE',
                     'message': 'Must be an allowed value',
                     'severity': 'ERROR'},
                    {'field': 'TISSUE_REMOVED_FOR_BARCODING',
                     'message': 'Must be an allowed value',
                     'severity': 'ERROR'},
                    {'field': 'TISSUE_FOR_BARCODING',
                     'message': 'Must be an allowed value',
                     'severity': 'ERROR'},
                    {'field': 'PURPOSE_OF_SPECIMEN',
                     'message': 'Must be an allowed value',
                     'severity': 'ERROR'},
                    {'field': 'HAZARD_GROUP',
                     'message': 'Must be an allowed value',
                     'severity': 'ERROR'},
                    {'field': 'REGULATORY_COMPLIANCE',
                     'message': 'Must be an allowed value',
                     'severity': 'ERROR'}]
        results = validate_allowed_values(self.sample1)
        self.assertEqual(results, expected)

        self.sample1.symbiont = "TARGET"
        self.sample1.organism_part = "SPORE"
        self.sample1.sex = "FEMALE"
        self.sample1.difficult_or_high_priority_sample = "DIFFICULT"
        self.sample1.specimen_id_risk = "Y"
        self.sample1.size_of_tissue_in_tube = "VS"
        self.sample1.tissue_removed_for_barcoding = "Y"
        self.sample1.tissue_for_barcoding = "SPLEEN"
        self.sample1.purpose_of_specimen = "RNA_SEQUENCING"
        self.sample1.hazard_group = "HG1"
        self.sample1.regulatory_compliance = "Y"
        results = validate_allowed_values(self.sample1)
        self.assertEqual(results, [])

        # Multiple values correct
        self.sample1.organism_part = "SPORE | MUSCLE | LEG"
        results = validate_allowed_values(self.sample1)
        self.assertEqual(results, [])

        # Multiple values incorrect
        self.sample1.organism_part = "SPORE | INVALID | NOTHING"
        results = validate_allowed_values(self.sample1)
        expected = [{'field': 'ORGANISM_PART',
                     'message': 'Must be an allowed value',
                     'severity': 'ERROR'}]
        self.assertEqual(results, expected)

    def test_validate_regexs(self):
        self.sample1 = SubmissionsSample(series="INVALID",
                                         time_of_collection="INVALID",
                                         rack_or_plate_id="AJV1234",
                                         tube_or_well_id="AJV5678",
                                         time_elapsed_from_collection_to_preservation="INVALID",
                                         row=1)
        expected = [{'field': 'SERIES',
                     'message': 'Does not match a specific pattern',
                     'severity': 'ERROR'},
                    {'field': 'RACK_OR_PLATE_ID',
                     'message': 'Does not match a specific pattern',
                     'severity': 'WARNING'},
                    {'field': 'TUBE_OR_WELL_ID',
                     'message': 'Does not match a specific pattern',
                     'severity': 'WARNING'},
                    {'field': 'TIME_OF_COLLECTION',
                     'message': 'Does not match a specific pattern',
                     'severity': 'ERROR'},
                    {'field': 'TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION',
                     'message': 'Does not match a specific pattern',
                     'severity': 'ERROR'}]

        results = validate_regexs(self.sample1)
        self.assertEqual(results, expected)

        self.sample1.series = "26"
        self.sample1.time_of_collection = "12:00"
        self.sample1.rack_or_plate_id = "AV87654321"
        self.sample1.tube_or_well_id = "AV12345678"
        self.sample1.time_elapsed_from_collection_to_preservation = "NOT_COLLECTED"
        results = validate_regexs(self.sample1)
        self.assertEqual(results, [])

    def test_validate_specimen_id(self):
        self.sample1 = SubmissionsSample(GAL="SANGER INSTITUTE",
                                         specimen_id="INVALID1234567",
                                         row=1)
        expected = [{'field': 'SPECIMEN_ID',
                     'message': 'Prefix does not match the required pattern for the GAL',
                     'severity': 'ERROR'}]

        results = validate_specimen_id(self.sample1)
        self.assertEqual(results, expected)

        # Correct prefix, wrong suffix
        self.sample1.specimen_id = "SAN_4_86723"
        expected = [{'field': 'SPECIMEN_ID',
                     'message': 'Suffix does not match the required pattern for the GAL',
                     'severity': 'ERROR'}]
        results = validate_specimen_id(self.sample1)
        self.assertEqual(results, expected)

        # Correct prefix and suffix
        self.sample1.specimen_id = "SAN1234567"
        results = validate_specimen_id(self.sample1)
        self.assertEqual(results, [])

        # Correct prefix, no suffix
        self.sample1.GAL = "UNIVERSITY OF DERBY"
        self.sample1.specimen_id = "UDUK12345"
        results = validate_specimen_id(self.sample1)
        self.assertEqual(results, [])

        # GAL not in list - don't validate
        self.sample1.GAL = "NEW GAL"
        self.sample1.specimen_id = "UDUK12345"
        results = validate_specimen_id(self.sample1)
        self.assertEqual(results, [])

    def test_validate_rack_plate_tube_well_not_both_na(self):
        self.sample1 = SubmissionsSample(rack_or_plate_id="NA",
                                         tube_or_well_id="NA",
                                         row=1)
        expected = [{'field': 'TUBE_OR_WELL_ID',
                     'message': 'Cannot be NA if RACK_OR_PLATE_ID is NA',
                     'severity': 'ERROR'}]

        results = validate_rack_plate_tube_well_not_both_na(self.sample1)
        self.assertEqual(results, expected)

        self.sample1.rack_or_plate_id = "RR12345678"
        self.sample1.tube_or_well_id = "TB12345678"
        results = validate_rack_plate_tube_well_not_both_na(self.sample1)
        self.assertEqual(results, [])

    def test_validate_rack_plate_tube_well_unique(self):
        sample1 = SubmissionsSample(rack_or_plate_id="RR12345678",
                                    tube_or_well_id="TB12345678",
                                    symbiont="TARGET",
                                    row=1)
        sample2 = SubmissionsSample(rack_or_plate_id="RR12345678",
                                    tube_or_well_id="TB12345678",
                                    symbiont="TARGET",
                                    row=2)
        manifest = SubmissionsManifest()
        sample1.manifest = manifest
        sample2.manifest = manifest
        manifest.reset_trackers()

        expected = [{'field': 'SYMBIONT',
                     'message': 'Must only be one target specimen id per rack/tube or plate/well',
                     'severity': 'ERROR'}]

        results = validate_rack_plate_tube_well_unique(sample1)
        self.assertEqual(results, expected)

        results = validate_rack_plate_tube_well_unique(sample2)
        self.assertEqual(results, expected)

        # Symbionts are allowed
        sample2.symbiont = "SYMBIONT"
        manifest.reset_trackers()
        results = validate_rack_plate_tube_well_unique(sample2)
        self.assertEqual(results, [])

    def test_validate_no_orphaned_symbionts(self):
        sample1 = SubmissionsSample(rack_or_plate_id="RR12345678",
                                    tube_or_well_id="TB12345678",
                                    symbiont="TARGET",
                                    row=1)
        sample2 = SubmissionsSample(rack_or_plate_id="RR99999999",
                                    tube_or_well_id="TB99999999",
                                    symbiont="SYMBIONT",
                                    row=2)
        manifest = SubmissionsManifest()
        sample1.manifest = manifest
        sample2.manifest = manifest
        manifest.reset_trackers()

        expected = [{'field': 'SYMBIONT',
                     'message': 'All symbionts must have a TARGET with ' +
                                'same rack/plate and tube/well',
                     'severity': 'ERROR'}]

        results = validate_no_orphaned_symbionts(sample1)
        self.assertEqual(results, [])

        results = validate_no_orphaned_symbionts(sample2)
        self.assertEqual(results, expected)

        # Symbiont has a target
        sample2.rack_or_plate_id = "RR12345678"
        sample2.tube_or_well_id = "TB12345678"
        manifest.reset_trackers()
        results = validate_no_orphaned_symbionts(sample2)
        self.assertEqual(results, [])

    def test_validate_no_specimens_with_different_taxons(self):
        sample1 = SubmissionsSample(specimen_id="SAN12345678",
                                    taxonomy_id=6344,
                                    symbiont="TARGET",
                                    row=1)
        sample2 = SubmissionsSample(specimen_id="SAN12345678",
                                    taxonomy_id=6355,
                                    symbiont="TARGET",
                                    row=2)
        manifest = SubmissionsManifest()
        sample1.manifest = manifest
        sample2.manifest = manifest
        manifest.reset_trackers()

        expected = [{'field': 'TAXON_ID',
                     'message': 'Targets must not use the same SPECIMEN_ID ' +
                                'with a different TAXON_ID',
                     'severity': 'ERROR'}]

        results = validate_no_specimens_with_different_taxons(sample1)
        self.assertEqual(results, [])

        results = validate_no_specimens_with_different_taxons(sample2)
        self.assertEqual(results, expected)

        # Correct
        sample2.taxonomy_id = 6344
        manifest.reset_trackers()
        results = validate_no_specimens_with_different_taxons(sample1)
        self.assertEqual(results, [])
        results = validate_no_specimens_with_different_taxons(sample2)
        self.assertEqual(results, [])

        # Valid for symbionts
        sample2.taxonomy_id = 6355
        sample2.symbiont = "SYMBIONT"
        manifest.reset_trackers()
        results = validate_no_specimens_with_different_taxons(sample1)
        self.assertEqual(results, [])
        results = validate_no_specimens_with_different_taxons(sample2)
        self.assertEqual(results, [])

    def test_validate_barcoding(self):
        sample1 = SubmissionsSample(tissue_removed_for_barcoding="N",
                                    plate_id_for_barcoding="PL12345678",
                                    tube_or_well_id_for_barcoding="TB87654321",
                                    tissue_for_barcoding="MUSCLE",
                                    barcode_plate_preservative="VINEGAR",
                                    row=1)

        expected = [{'field': 'PLATE_ID_FOR_BARCODING',
                     'message': 'If TISSUE_REMOVED_FOR_BARCODING is N, other ' +
                                'barcoding fields must be NOT_APPLICABLE',
                     'severity': 'ERROR'},
                    {'field': 'TUBE_OR_WELL_ID_FOR_BARCODING',
                     'message': 'If TISSUE_REMOVED_FOR_BARCODING is N, other ' +
                                'barcoding fields must be NOT_APPLICABLE',
                     'severity': 'ERROR'},
                    {'field': 'TISSUE_FOR_BARCODING',
                     'message': 'If TISSUE_REMOVED_FOR_BARCODING is N, other ' +
                                'barcoding fields must be NOT_APPLICABLE',
                     'severity': 'ERROR'},
                    {'field': 'BARCODE_PLATE_PRESERVATIVE',
                     'message': 'If TISSUE_REMOVED_FOR_BARCODING is N, other ' +
                                'barcoding fields must be NOT_APPLICABLE',
                     'severity': 'ERROR'}]

        results = validate_barcoding(sample1)
        self.assertEqual(results, expected)

        # Correct
        sample1.tissue_removed_for_barcoding = 'Y'
        results = validate_barcoding(sample1)
        self.assertEqual(results, [])

    def test_whole_organisms_unique(self):
        sample1 = SubmissionsSample(specimen_id="SAN1234567",
                                    organism_part="WHOLE_ORGANISM",
                                    row=1)
        sample2 = SubmissionsSample(specimen_id="SAN1234567",
                                    organism_part="WHOLE_ORGANISM",
                                    row=2)
        manifest = SubmissionsManifest()
        sample1.manifest = manifest
        sample2.manifest = manifest
        manifest.reset_trackers()

        expected = [{'field': 'SPECIMEN_ID',
                     'message': 'WHOLE_ORGANISM can only be used once',
                     'severity': 'ERROR'}]

        results = validate_whole_organisms_unique(sample1)
        self.assertEqual(results, expected)

        results = validate_whole_organisms_unique(sample2)
        self.assertEqual(results, expected)

        # Symbionts are allowed
        sample2.specimen_id = "SAN7654321"
        manifest.reset_trackers()
        results = validate_whole_organisms_unique(sample2)
        self.assertEqual(results, [])

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

        mock_response_from_tolid_specimen = [{
            "specimenId": "SAN0000100",
            "tolIds": [{
                "species": {
                    "commonName": "lugworm",
                    "currentHighestTolidNumber": 2,
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
                "tolId": "wuAreMari1"
            }]
        }]
        responses.add(responses.GET, os.environ['TOLID_URL'] + '/specimens/SAN0000100',
                      json=mock_response_from_tolid_specimen, status=200)

        mock_response_from_sts = {}  # Only interested in status codes
        responses.add(responses.GET, os.environ['STS_URL'] + '/samples/detail',
                      json=mock_response_from_sts, status=400)

        self.manifest1 = SubmissionsManifest()
        self.manifest1.project_name = "TestProj1"
        self.manifest1.sts_manifest_id = "1234-5678"
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
                                         specimen_id="SAN0000100",
                                         taxonomy_id=6344,
                                         voucher_id="voucher1",
                                         rack_or_plate_id="RR12345678",
                                         tube_or_well_id="TB12345678",
                                         row=1)
        self.sample1.manifest = self.manifest1
        db.session.add(self.manifest1)
        db.session.add(self.sample1)

        number_of_errors, results = validate_manifest(self.manifest1)
        self.assertEqual(number_of_errors, 0)
        self.assertEqual(len(results), 1)
        self.assertEqual(len(results[0]["results"]), 0)

        # Cause a validation failure
        self.sample1.family = ""
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
                     'message': 'Must not be empty',
                     'severity': 'ERROR'},
                    {'field': 'LIFESTAGE',
                     'message': 'Must be in allowed values',
                     'severity': 'ERROR'},
                    {'field': 'COLLECTED_BY', 'message': 'Must not be empty',
                     'severity': 'ERROR'},
                    {'field': 'DATE_OF_COLLECTION', 'message': 'Must match specific pattern',
                     'severity': 'ERROR'},
                    {'field': 'COLLECTION_LOCATION', 'message': 'Must be in allowed values',
                     'severity': 'ERROR'},
                    {'field': 'DECIMAL_LATITUDE', 'message': 'Must not be empty',
                     'severity': 'ERROR'},
                    {'field': 'DECIMAL_LONGITUDE', 'message': 'Must match specific pattern',
                     'severity': 'ERROR'},
                    {'field': 'IDENTIFIED_BY', 'message': 'Must not be empty',
                     'severity': 'ERROR'},
                    {'field': 'DEPTH', 'message': 'Must match specific pattern',
                     'severity': 'ERROR'},
                    {'field': 'ELEVATION', 'message': 'Must match specific pattern',
                     'severity': 'ERROR'},
                    {'field': 'HABITAT', 'message': 'Must not be empty',
                     'severity': 'ERROR'},
                    {'field': 'IDENTIFIER_AFFILIATION', 'message': 'Must not be empty',
                     'severity': 'ERROR'},
                    {'field': 'SEX', 'message': 'Must not be empty',
                     'severity': 'ERROR'},
                    {'field': 'COLLECTOR_AFFILIATION', 'message': 'Must not be empty',
                     'severity': 'ERROR'},
                    {'field': 'GAL', 'message': 'Must be in allowed values',
                     'severity': 'ERROR'},
                    {'field': 'VOUCHER_ID', 'message': 'Must not be empty',
                     'severity': 'ERROR'},
                    {'field': 'SPECIMEN_ID', 'message': 'Must not be empty',
                     'severity': 'ERROR'},
                    {'field': 'GAL_SAMPLE_ID', 'message': 'Must not be empty',
                     'severity': 'ERROR'}]

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
        sample.decimal_latitude = "NOT_COLLECTED"
        sample.decimal_longitude = "-1.98765432"
        sample.habitat = "WOODLAND"
        sample.identified_by = "JO IDENTIFIER"
        sample.identifier_affiliation = "THE IDENTIFIER INSTITUTE"
        sample.voucher_id = "voucher1"
        sample.elevation = "1500"
        sample.depth = "1000"
        sample.relationship = "child of 1234"
        sample.symbiont = "TARGET"
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
                     "message": "Is not ENA submittable",
                     'severity': 'ERROR'},
                    {'field': 'SCIENTIFIC_NAME',
                     'message': 'Must match ENA (expected Arenicola marina2)',
                     'severity': 'ERROR'}]

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
                     "message": "Is not known at ENA",
                     'severity': 'ERROR'}]

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
                     "message": "Communication with ENA has failed with status code 500",
                     'severity': 'ERROR'}]

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
                     "message": "Species not known in the ToLID service",
                     'severity': 'WARNING'}]

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
                     "message": "Communication failed with the ToLID service: status code 500",
                     'severity': 'ERROR'}]

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
                     + "(expecting Arenicola marina)",
                     'severity': 'ERROR'},
                    {"field": "GENUS",
                     "message": "Does not match that in the ToLID service (expecting Arenicola)",
                     'severity': 'ERROR'},
                    {"field": "FAMILY",
                     "message": "Does not match that in the ToLID service "
                     + "(expecting Arenicolidae)",
                     'severity': 'ERROR'},
                    {"field": "ORDER_OR_GROUP",
                     "message": "Does not match that in the ToLID service (expecting None)",
                     'severity': 'ERROR'}]

        self.assertEqual(results, expected)

    @responses.activate
    def test_validate_specimen_tolid_correct(self):
        mock_response_from_tolid = [{
            "specimenId": "SAN0001234",
            "tolIds": [{
                "species": {
                    "commonName": "lugworm",
                    "currentHighestTolidNumber": 2,
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
                "tolId": "wuAreMari1"
            }]
        }]
        responses.add(responses.GET, os.environ['TOLID_URL'] + '/specimens/SAN0001234',
                      json=mock_response_from_tolid, status=200)

        sample = SubmissionsSample()
        sample.specimen_id = "SAN0001234"
        sample.taxonomy_id = 6344

        results = validate_specimen_against_tolid(sample)
        expected = []

        self.assertEqual(results, expected)

    # The real version of this does a call to the ToLID service. We mock that call here
    @responses.activate
    def test_validate_specimen_tolid_species_missing(self):
        mock_response_from_tolid = []
        responses.add(responses.GET, os.environ['TOLID_URL'] + '/specimens/SAN0001234',
                      json=mock_response_from_tolid, status=404)

        sample = SubmissionsSample()
        sample.specimen_id = "SAN0001234"
        sample.taxonomy_id = 6344

        results = validate_specimen_against_tolid(sample)
        self.assertEqual(results, [])

    # The real version of this does a call to the ToLID service. We mock that call here
    @responses.activate
    def test_validate_specimen_tolid_cant_communicate(self):
        mock_response_from_tolid = []
        responses.add(responses.GET, os.environ['TOLID_URL'] + '/specimens/SAN0001234',
                      json=mock_response_from_tolid, status=500)

        sample = SubmissionsSample()
        sample.specimen_id = "SAN0001234"
        sample.taxonomy_id = 6344

        results = validate_specimen_against_tolid(sample)
        expected = [{"field": "SPECIMEN_ID",
                     "message": "Communication failed with the ToLID service: status code 500",
                     'severity': 'ERROR'}]

        self.assertEqual(results, expected)

    # The real version of this does a call to the ToLID service. We mock that call here
    @responses.activate
    def test_validate_specimen_tolid_taxon_mismatch(self):
        mock_response_from_tolid = [{
            "specimenId": "SAN0001234",
            "tolIds": [{
                "species": {
                    "commonName": "lugworm",
                    "currentHighestTolidNumber": 2,
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
                "tolId": "wuAreMari1"
            }, {
                "species": {
                    "commonName": "pugworm",
                    "currentHighestTolidNumber": 2,
                    "family": "Arenicolidae",
                    "genus": "Arenicola",
                    "kingdom": "Metazoa",
                    "order": "Capitellida",
                    "phylum": "Annelida",
                    "prefix": "wuAreMarp",
                    "scientificName": "Arenicola marinp",
                    "taxaClass": "Polychaeta",
                    "taxonomyId": 6355
                },
                "tolId": "wuAreMari1"
            }]
        }]
        responses.add(responses.GET, os.environ['TOLID_URL'] + '/specimens/SAN0001234',
                      json=mock_response_from_tolid, status=200)
        sample = SubmissionsSample()
        sample.specimen_id = "SAN0001234"
        sample.taxonomy_id = 6366
        results = validate_specimen_against_tolid(sample)
        expected = [{"field": "SPECIMEN_ID",
                     "message": "Has been used before but with different taxonomy ID",
                     'severity': 'ERROR'}]

        self.assertEqual(results, expected)

    def test_validate_specimen_tolid_symbiont(self):
        sample = SubmissionsSample()
        sample.specimen_id = "SAN0001234"
        sample.taxonomy_id = 6344
        sample.symbiont = 'SYMBIONT'

        results = validate_specimen_against_tolid(sample)

        self.assertEqual(results, [])

    @responses.activate
    def test_validate_rack_plate_tube_well_sts_exists(self):
        mock_response_from_sts = {}  # Only interested in status codes
        responses.add(responses.GET, os.environ['STS_URL'] + '/samples/detail',
                      json=mock_response_from_sts, status=200)

        sample = SubmissionsSample()
        sample.rack_or_plate_id = "RR12345678"
        sample.tube_or_well_id = "TB12345678"

        results = validate_sts_rack_plate_tube_well(sample)
        expected = [{"field": "TUBE_OR_WELL_ID",
                     "message": "Already exists in STS so cannot be used again",
                     'severity': 'ERROR'}]

        self.assertEqual(results, expected)

    @responses.activate
    def test_validate_rack_plate_tube_well_sts_not_exists(self):
        mock_response_from_sts = {}  # Only interested in status codes
        responses.add(responses.GET, os.environ['STS_URL'] + '/samples/detail',
                      json=mock_response_from_sts, status=400)

        sample = SubmissionsSample()
        sample.rack_or_plate_id = "RR12345678"
        sample.tube_or_well_id = "TB12345678"

        results = validate_sts_rack_plate_tube_well(sample)
        expected = []

        self.assertEqual(results, expected)

    @responses.activate
    def test_validate_rack_plate_tube_well_sts_cant_communicate(self):
        mock_response_from_sts = {}  # Only interested in status codes
        responses.add(responses.GET, os.environ['STS_URL'] + '/samples/detail',
                      json=mock_response_from_sts, status=500)

        sample = SubmissionsSample()
        sample.rack_or_plate_id = "RR12345678"
        sample.tube_or_well_id = "TB12345678"

        results = validate_sts_rack_plate_tube_well(sample)
        expected = [{"field": "TUBE_OR_WELL_ID",
                     "message": "Communication failed with the STS service: status code 500",
                     'severity': 'ERROR'}]

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
                                  "message": "A ToLID has not been generated",
                                  'severity': 'WARNING'}]},
                    {"row": 2,
                     "results": [{"field": "TAXON_ID",
                                  "message": "A ToLID has not been generated",
                                  'severity': 'WARNING'}]}]

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
        sample.symbiont = "TARGET"
        sample.manifest = manifest

        sample = SubmissionsSample()
        sample.row = 2
        sample.specimen_id = "specimen1234"
        sample.taxonomy_id = 2720616
        sample.scientific_name = "Trichosporum symbioticum"
        sample.family = "Piedraiaceae"
        sample.genus = "Trichosporum"
        sample.order_or_group = "Capnodiales"
        sample.common_name = "None"
        sample.lifestage = "ADULT"
        sample.sex = "FEMALE"
        sample.organism_part = "SPORE"
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
        sample.symbiont = "SYMBIONT"
        sample.manifest = manifest

        specimen = SubmissionsSpecimen()
        specimen.specimen_id = "specimen1234"
        specimen.biosample_accession = "SAMEA12345678"
        db.session.add(specimen)
        db.session.commit()

        error_count, results = set_relationships_for_manifest(manifest)
        self.assertEqual("SAMEA12345678", manifest.samples[0].sample_derived_from)
        self.assertEqual(None, manifest.samples[0].sample_same_as)
        self.assertEqual(None, manifest.samples[0].sample_symbiont_of)
        self.assertEqual(None, manifest.samples[1].sample_derived_from)
        self.assertEqual(None, manifest.samples[1].sample_same_as)
        self.assertEqual("SAMEA12345678", manifest.samples[1].sample_symbiont_of)
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

        self.assertEqual("SAMEA8521239", specimen_manifest.samples[0].biosample_accession)

        # Check the new specimen
        specimen = db.session.query(SubmissionsSpecimen) \
            .filter(SubmissionsSpecimen.specimen_id == "specimen1234") \
            .one_or_none()

        self.assertEqual("SAMEA8521239", specimen.biosample_accession)

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
                                        'message': 'Cannot connect to ENA service '
                                        + '(status code 403)',
                                        'severity': 'ERROR'}],
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
        self.assertEqual("SAMEA8521239", sample.biosample_accession)
        self.assertEqual("ERS6206028", sample.sra_accession)
        self.assertEqual("ERA3819349", sample.submission_accession)
        self.assertEqual("SAMEA8521239B", sample2.biosample_accession)
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
                                  'message': 'Cannot connect to ENA service (status code 404)',
                                  'severity': 'ERROR'}],
                     'row': 1}]
        self.assertEqual(1, number_of_errors)
        self.assertEqual(expected, results)

        self.assertEqual(None, sample.biosample_accession)
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
                                  'message': 'Error returned from ENA service',
                                  'severity': 'ERROR'}],
                     'row': 1}]
        self.assertEqual(1, number_of_errors)
        self.assertEqual(expected, results)
        self.assertEqual(None, sample.biosample_accession)
        self.assertEqual(None, sample.sra_accession)
        self.assertEqual(None, sample.submission_accession)
        self.assertEqual(False, manifest.submission_status)
        self.assertTrue(sample.submission_error is not None)


if __name__ == '__main__':
    import unittest
    unittest.main()
