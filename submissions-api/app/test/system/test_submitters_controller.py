# SPDX-FileCopyrightText: 2021 Genome Research Ltd.
#
# SPDX-License-Identifier: MIT

from __future__ import absolute_import

import datetime
import os
from test.system import BaseTestCase
from unittest.mock import patch

from main.model import SubmissionsManifest, SubmissionsSample, \
    SubmissionsSpecimen, db

import responses


class TestSubmittersController(BaseTestCase):

    def test_submit_manifest_json(self):
        # No authorisation token given
        body = []
        response = self.client.open(
            '/api/v1/manifests',
            method='POST',
            json=body)
        self.assert401(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Invalid authorisation token given
        body = []
        response = self.client.open(
            '/api/v1/manifests',
            method='POST',
            headers={'api-key': '12345678'},
            json=body)
        self.assert401(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Body empty
        body = {}
        response = self.client.open(
            '/api/v1/manifests',
            method='POST',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert400(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        body = {'samples': [{
            'row': 1,
            'SPECIMEN_ID': 'SAN1234567',
            'TAXON_ID': 6344,
            'SCIENTIFIC_NAME': 'Arenicola marina',
            'GENUS': 'Arenicola',
            'FAMILY': 'Arenicolidae',
            'ORDER_OR_GROUP': 'Scolecida',
            'COMMON_NAME': 'lugworm',
            'LIFESTAGE': 'ADULT',
            'SEX': 'FEMALE',
            'ORGANISM_PART': 'MUSCLE',
            'GAL': 'SANGER INSTITUTE',
            'GAL_SAMPLE_ID': 'SAN0000100',
            'COLLECTED_BY': 'ALEX COLLECTOR',
            'COLLECTOR_AFFILIATION': 'THE COLLECTOR INSTITUTE',
            'DATE_OF_COLLECTION': '2020-09-01',
            'COLLECTION_LOCATION': 'UNITED KINGDOM | DARK FOREST',
            'DECIMAL_LATITUDE': '+50.12345678',
            'DECIMAL_LONGITUDE': 'NOT_PROVIDED',
            'HABITAT': 'Woodland',
            'IDENTIFIED_BY': 'JO IDENTIFIER',
            'IDENTIFIER_AFFILIATION': 'THE IDENTIFIER INSTITUTE',
            'VOUCHER_ID': 'voucher1',
            'OTHER_INFORMATION': 'Interesting',
            'ELEVATION': '',  # Expect this to be set to None
            'SERIES': '1',
            'RACK_OR_PLATE_ID': 'RR12345678',
            'TUBE_OR_WELL_ID': 'TU12345678',
            'TAXON_REMARKS': 'nice',
            'INFRASPECIFIC_EPITHET': 'ie1',
            'COLLECTOR_SAMPLE_ID': 'mysample1',
            'GRID_REFERENCE': 'TL 1234 5678',
            'TIME_OF_COLLECTION': '12:00',
            'DESCRIPTION_OF_COLLECTION_METHOD': 'picked it',
            'DIFFICULT_OR_HIGH_PRIORITY_SAMPLE': 'Y',
            'IDENTIFIED_HOW': 'looking',
            'SPECIMEN_ID_RISK': 'Y',
            'PRESERVED_BY': 'A Freezer',
            'PRESERVER_AFFILIATION': 'cold storage ltd',
            'PRESERVATION_APPROACH': 'Freezing',
            'PRESERVATIVE_SOLUTION': 'Water',
            'TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION': '60',
            'DATE_OF_PRESERVATION': '2021-04-04',
            'SIZE_OF_TISSUE_IN_TUBE': 'VS',
            'TISSUE_REMOVED_FOR_BARCODING': 'Y',
            'PLATE_ID_FOR_BARCODING': 'plate1',
            'TUBE_OR_WELL_ID_FOR_BARCODING': 'well1',
            'TISSUE_FOR_BARCODING': 'LEG',
            'BARCODE_PLATE_PRESERVATIVE': 'ethanol',
            'PURPOSE_OF_SPECIMEN': 'REFERENCE_GENOME',
            'HAZARD_GROUP': 'HG1',
            'REGULATORY_COMPLIANCE': 'Y',
            'ORIGINAL_COLLECTION_DATE': '2021-05-05',
            'ORIGINAL_GEOGRAPHIC_LOCATION': 'United Kingdom | Light Forest',
            'BARCODE_HUB': 'SANGER INSTITUTE',
            'EXTRA_FIELD': 'extra1',
            'EXTRA_FIELD_2': None}
        ]}
        # Not a submitter
        response = self.client.open(
            '/api/v1/manifests',
            method='POST',
            headers={'api-key': self.user1.api_key},
            json=body)
        self.assert403(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Correct, full JSON
        response = self.client.open(
            '/api/v1/manifests',
            method='POST',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        expected = {'manifestId': 1,
                    'submissionStatus': None,
                    'projectName': 'ToL',  # Default - not given in body
                    'stsManifestId': None,  # Default - not given in body
                    'samples': [
                        {'row': 1,
                         'SPECIMEN_ID': 'SAN1234567',
                         'TAXON_ID': 6344,
                         'SCIENTIFIC_NAME': 'Arenicola marina',
                         'GENUS': 'Arenicola',
                         'FAMILY': 'Arenicolidae',
                         'ORDER_OR_GROUP': 'Scolecida',
                         'COMMON_NAME': 'lugworm',
                         'LIFESTAGE': 'ADULT',
                         'SEX': 'FEMALE',
                         'ORGANISM_PART': 'MUSCLE',
                         'GAL': 'SANGER INSTITUTE',
                         'GAL_SAMPLE_ID': 'SAN0000100',
                         'COLLECTED_BY': 'ALEX COLLECTOR',
                         'COLLECTOR_AFFILIATION': 'THE COLLECTOR INSTITUTE',
                         'DATE_OF_COLLECTION': '2020-09-01',
                         'COLLECTION_LOCATION': 'UNITED KINGDOM | DARK FOREST',
                         'DECIMAL_LATITUDE': '+50.12345678',
                         'DECIMAL_LONGITUDE': 'NOT_PROVIDED',
                         'HABITAT': 'Woodland',
                         'IDENTIFIED_BY': 'JO IDENTIFIER',
                         'IDENTIFIER_AFFILIATION': 'THE IDENTIFIER INSTITUTE',
                         'VOUCHER_ID': 'voucher1',
                         'OTHER_INFORMATION': 'Interesting',
                         'ELEVATION': None,
                         'DEPTH': None,
                         'RELATIONSHIP': None,
                         'SYMBIONT': None,
                         'CULTURE_OR_STRAIN_ID': None,
                         'SERIES': '1',
                         'RACK_OR_PLATE_ID': 'RR12345678',
                         'TUBE_OR_WELL_ID': 'TU12345678',
                         'TAXON_REMARKS': 'nice',
                         'INFRASPECIFIC_EPITHET': 'ie1',
                         'COLLECTOR_SAMPLE_ID': 'mysample1',
                         'GRID_REFERENCE': 'TL 1234 5678',
                         'TIME_OF_COLLECTION': '12:00',
                         'DESCRIPTION_OF_COLLECTION_METHOD': 'picked it',
                         'DIFFICULT_OR_HIGH_PRIORITY_SAMPLE': 'Y',
                         'IDENTIFIED_HOW': 'looking',
                         'SPECIMEN_ID_RISK': 'Y',
                         'PRESERVED_BY': 'A Freezer',
                         'PRESERVER_AFFILIATION': 'cold storage ltd',
                         'PRESERVATION_APPROACH': 'Freezing',
                         'PRESERVATIVE_SOLUTION': 'Water',
                         'TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION': '60',
                         'DATE_OF_PRESERVATION': '2021-04-04',
                         'SIZE_OF_TISSUE_IN_TUBE': 'VS',
                         'TISSUE_REMOVED_FOR_BARCODING': 'Y',
                         'PLATE_ID_FOR_BARCODING': 'plate1',
                         'TUBE_OR_WELL_ID_FOR_BARCODING': 'well1',
                         'TISSUE_FOR_BARCODING': 'LEG',
                         'BARCODE_PLATE_PRESERVATIVE': 'ethanol',
                         'PURPOSE_OF_SPECIMEN': 'REFERENCE_GENOME',
                         'HAZARD_GROUP': 'HG1',
                         'REGULATORY_COMPLIANCE': 'Y',
                         'ORIGINAL_COLLECTION_DATE': '2021-05-05',
                         'ORIGINAL_GEOGRAPHIC_LOCATION': 'United Kingdom | Light Forest',
                         'BARCODE_HUB': 'SANGER INSTITUTE',
                         'EXTRA_FIELD': 'extra1',
                         'tolId': None,
                         'biosampleAccession': None,
                         'sraAccession': None,
                         'submissionAccession': None,
                         'submissionError': None,
                         'sampleSameAs': None,
                         'sampleDerivedFrom': None,
                         'sampleSymbiontOf': None}
                    ]}
        print(response.json)
        self.assertEqual(expected, response.json)

        # Correct, symbiont-only JSON
        body = {'samples': [{
            'row': 1,
            'SPECIMEN_ID': 'SAN1234567',
            'TAXON_ID': 6344,
            'SCIENTIFIC_NAME': 'Arenicola marina',
            'LIFESTAGE': 'ADULT',
            'SEX': 'FEMALE',
            'ORGANISM_PART': 'MUSCLE',
            'SYMBIONT': 'SYMBIONT'}
        ]}
        response = self.client.open(
            '/api/v1/manifests',
            method='POST',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        expected = {'manifestId': 2,
                    'submissionStatus': None,
                    'projectName': 'ToL',  # Default - not given in body
                    'stsManifestId': None,  # Default - not given in body
                    'samples': [
                        {'row': 1,
                         'SPECIMEN_ID': 'SAN1234567',
                         'TAXON_ID': 6344,
                         'SCIENTIFIC_NAME': 'Arenicola marina',
                         'GENUS': None,
                         'FAMILY': None,
                         'ORDER_OR_GROUP': None,
                         'COMMON_NAME': None,
                         'LIFESTAGE': 'ADULT',
                         'SEX': 'FEMALE',
                         'ORGANISM_PART': 'MUSCLE',
                         'GAL': None,
                         'GAL_SAMPLE_ID': None,
                         'COLLECTED_BY': None,
                         'COLLECTOR_AFFILIATION': None,
                         'DATE_OF_COLLECTION': None,
                         'COLLECTION_LOCATION': None,
                         'DECIMAL_LATITUDE': None,
                         'DECIMAL_LONGITUDE': None,
                         'HABITAT': None,
                         'IDENTIFIED_BY': None,
                         'IDENTIFIER_AFFILIATION': None,
                         'VOUCHER_ID': None,
                         'OTHER_INFORMATION': None,
                         'ELEVATION': None,
                         'DEPTH': None,
                         'RELATIONSHIP': None,
                         'SYMBIONT': 'SYMBIONT',
                         'CULTURE_OR_STRAIN_ID': None,
                         'SERIES': None,
                         'RACK_OR_PLATE_ID': None,
                         'TUBE_OR_WELL_ID': None,
                         'TAXON_REMARKS': None,
                         'INFRASPECIFIC_EPITHET': None,
                         'COLLECTOR_SAMPLE_ID': None,
                         'GRID_REFERENCE': None,
                         'TIME_OF_COLLECTION': None,
                         'DESCRIPTION_OF_COLLECTION_METHOD': None,
                         'DIFFICULT_OR_HIGH_PRIORITY_SAMPLE': None,
                         'IDENTIFIED_HOW': None,
                         'SPECIMEN_ID_RISK': None,
                         'PRESERVED_BY': None,
                         'PRESERVER_AFFILIATION': None,
                         'PRESERVATION_APPROACH': None,
                         'PRESERVATIVE_SOLUTION': None,
                         'TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION': None,
                         'DATE_OF_PRESERVATION': None,
                         'SIZE_OF_TISSUE_IN_TUBE': None,
                         'TISSUE_REMOVED_FOR_BARCODING': None,
                         'PLATE_ID_FOR_BARCODING': None,
                         'TUBE_OR_WELL_ID_FOR_BARCODING': None,
                         'TISSUE_FOR_BARCODING': None,
                         'BARCODE_PLATE_PRESERVATIVE': None,
                         'PURPOSE_OF_SPECIMEN': None,
                         'HAZARD_GROUP': None,
                         'REGULATORY_COMPLIANCE': None,
                         'ORIGINAL_COLLECTION_DATE': None,
                         'ORIGINAL_GEOGRAPHIC_LOCATION': None,
                         'BARCODE_HUB': None,
                         'tolId': None,
                         'biosampleAccession': None,
                         'sraAccession': None,
                         'submissionAccession': None,
                         'submissionError': None,
                         'sampleSameAs': None,
                         'sampleDerivedFrom': None,
                         'sampleSymbiontOf': None}
                    ]}
        print(response.json)
        self.assertEqual(expected, response.json)

    def test_get_manifest(self):

        body = {'samples': [{
            'row': 1,
            'SPECIMEN_ID': 'SAN1234567',
            'TAXON_ID': 6344,
            'SCIENTIFIC_NAME': 'Arenicola marina',
            'GENUS': 'Arenicola',
            'FAMILY': 'Arenicolidae',
            'ORDER_OR_GROUP': 'Scolecida',
            'COMMON_NAME': 'lugworm',
            'LIFESTAGE': 'ADULT',
            'SEX': 'FEMALE',
            'ORGANISM_PART': 'MUSCLE',
            'GAL': 'SANGER INSTITUTE',
            'GAL_SAMPLE_ID': 'SAN0000100',
            'COLLECTED_BY': 'ALEX COLLECTOR',
            'COLLECTOR_AFFILIATION': 'THE COLLECTOR INSTITUTE',
            'DATE_OF_COLLECTION': '2020-09-01',
            'COLLECTION_LOCATION': 'UNITED KINGDOM | DARK FOREST',
            'DECIMAL_LATITUDE': 'NOT_PROVIDED',
            'DECIMAL_LONGITUDE': '-1.98765432',
            'HABITAT': 'Woodland',
            'IDENTIFIED_BY': 'JO IDENTIFIER',
            'IDENTIFIER_AFFILIATION': 'THE IDENTIFIER INSTITUTE',
            'VOUCHER_ID': 'voucher1',
            'ELEVATION': None,  # Test None is same as missing
            'DEPTH': ''}],  # Test '' is the same as missing
            'projectName': 'TestProj',
            'stsManifestId': '1234-4321'
        }

        # Submit the manifest
        response = self.client.open(
            '/api/v1/manifests',
            method='POST',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # No authorisation token given
        body = []
        response = self.client.open(
            '/api/v1/manifests/1',
            method='GET',
            json=body)
        self.assert401(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Invalid authorisation token given
        body = []
        response = self.client.open(
            '/api/v1/manifests/1',
            method='GET',
            headers={'api-key': '12345678'},
            json=body)
        self.assert401(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Incorrect manifest ID
        body = {}
        response = self.client.open(
            '/api/v1/manifests/2',
            method='GET',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert404(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Not a submitter
        response = self.client.open(
            '/api/v1/manifests/1',
            method='GET',
            headers={'api-key': self.user1.api_key},
            json=body)
        self.assert403(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Corect - should validate and return errors
        response = self.client.open(
            '/api/v1/manifests/1',
            method='GET',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        expected = {'manifestId': 1,
                    'submissionStatus': None,
                    'projectName': 'TestProj',
                    'stsManifestId': '1234-4321',
                    'samples': [{
                        'row': 1,
                        'SPECIMEN_ID': 'SAN1234567',
                        'TAXON_ID': 6344,
                        'SCIENTIFIC_NAME': 'Arenicola marina',
                        'GENUS': 'Arenicola',
                        'FAMILY': 'Arenicolidae',
                        'ORDER_OR_GROUP': 'Scolecida',
                        'COMMON_NAME': 'lugworm',
                        'LIFESTAGE': 'ADULT',
                        'SEX': 'FEMALE',
                        'ORGANISM_PART': 'MUSCLE',
                        'GAL': 'SANGER INSTITUTE',
                        'GAL_SAMPLE_ID': 'SAN0000100',
                        'COLLECTED_BY': 'ALEX COLLECTOR',
                        'COLLECTOR_AFFILIATION': 'THE COLLECTOR INSTITUTE',
                        'DATE_OF_COLLECTION': '2020-09-01',
                        'COLLECTION_LOCATION': 'UNITED KINGDOM | DARK FOREST',
                        'DECIMAL_LATITUDE': 'NOT_PROVIDED',
                        'DECIMAL_LONGITUDE': '-1.98765432',
                        'HABITAT': 'Woodland',
                        'IDENTIFIED_BY': 'JO IDENTIFIER',
                        'IDENTIFIER_AFFILIATION': 'THE IDENTIFIER INSTITUTE',
                        'VOUCHER_ID': 'voucher1',
                        'OTHER_INFORMATION': None,
                        'DEPTH': None,
                        'ELEVATION': None,
                        'RELATIONSHIP': None,
                        'SYMBIONT': None,
                        'CULTURE_OR_STRAIN_ID': None,
                        'SERIES': None,
                        'RACK_OR_PLATE_ID': None,
                        'TUBE_OR_WELL_ID': None,
                        'TAXON_REMARKS': None,
                        'INFRASPECIFIC_EPITHET': None,
                        'COLLECTOR_SAMPLE_ID': None,
                        'GRID_REFERENCE': None,
                        'TIME_OF_COLLECTION': None,
                        'DESCRIPTION_OF_COLLECTION_METHOD': None,
                        'DIFFICULT_OR_HIGH_PRIORITY_SAMPLE': None,
                        'IDENTIFIED_HOW': None,
                        'SPECIMEN_ID_RISK': None,
                        'PRESERVED_BY': None,
                        'PRESERVER_AFFILIATION': None,
                        'PRESERVATION_APPROACH': None,
                        'PRESERVATIVE_SOLUTION': None,
                        'TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION': None,
                        'DATE_OF_PRESERVATION': None,
                        'SIZE_OF_TISSUE_IN_TUBE': None,
                        'TISSUE_REMOVED_FOR_BARCODING': None,
                        'PLATE_ID_FOR_BARCODING': None,
                        'TUBE_OR_WELL_ID_FOR_BARCODING': None,
                        'TISSUE_FOR_BARCODING': None,
                        'BARCODE_PLATE_PRESERVATIVE': None,
                        'PURPOSE_OF_SPECIMEN': None,
                        'HAZARD_GROUP': None,
                        'REGULATORY_COMPLIANCE': None,
                        'ORIGINAL_COLLECTION_DATE': None,
                        'ORIGINAL_GEOGRAPHIC_LOCATION': None,
                        'BARCODE_HUB': None,
                        'tolId': None,
                        'biosampleAccession': None,
                        'sraAccession': None,
                        'submissionAccession': None,
                        'submissionError': None,
                        'sampleSameAs': None,
                        'sampleDerivedFrom': None,
                        'sampleSymbiontOf': None}
                    ]}
        self.assertEqual(expected, response.json)

    def test_get_manifests(self):

        manifest1 = SubmissionsManifest()
        manifest1.sts_manifest_id = '123-456-789'
        manifest1.project_name = 'WowProj'
        manifest1.submission_status = True
        manifest1.created_at = datetime.datetime(2020, 5, 17)
        manifest1.user = self.user1
        db.session.add(manifest1)
        manifest2 = SubmissionsManifest()
        manifest2.sts_manifest_id = '987-654-321'
        manifest2.project_name = 'DudProj'
        manifest2.submission_status = False
        manifest2.created_at = datetime.datetime(2021, 6, 18)
        manifest2.user = self.user2
        sample1 = SubmissionsSample(collected_by='ALEX COLLECTOR',
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
                                    GAL_sample_id='SAN0000100',
                                    genus='Arenicola',
                                    habitat='Woodland',
                                    identified_by='JO IDENTIFIER',
                                    identifier_affiliation='THE IDENTIFIER INSTITUTE',
                                    lifestage='ADULT',
                                    organism_part='MUSCLE',
                                    order_or_group='Scolecida',
                                    relationship='child of SAMEA1234567',
                                    scientific_name='Arenicola marina',
                                    sex='FEMALE',
                                    specimen_id='SAN0000100',
                                    taxonomy_id=6344,
                                    voucher_id='voucher1',
                                    row=1)
        sample1.manifest = manifest1
        db.session.add(manifest2)
        db.session.commit()

        # No authorisation token given
        body = []
        response = self.client.open(
            '/api/v1/manifests',
            method='GET',
            json=body)
        self.assert401(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Invalid authorisation token given
        body = []
        response = self.client.open(
            '/api/v1/manifests',
            method='GET',
            headers={'api-key': '12345678'},
            json=body)
        self.assert401(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Not a submitter
        response = self.client.open(
            '/api/v1/manifests',
            method='GET',
            headers={'api-key': self.user1.api_key},
            json=body)
        self.assert403(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Correct - should validate and return errors
        response = self.client.open(
            '/api/v1/manifests',
            method='GET',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        expected = [{'manifestId': 2,
                     'submissionStatus': False,
                     'projectName': 'DudProj',
                     'stsManifestId': '987-654-321',
                     'createdAt': '2021-06-18T00:00:00Z',
                     'numberOfSamples': 0,
                     'user': {'email': 'test_user_admin@sanger.ac.uk',
                              'name': 'test_user_admin',
                              'organisation': 'Sanger Institute',
                              'roles': [{'role': 'admin'}]}},
                    {'manifestId': 1,
                     'submissionStatus': True,
                     'projectName': 'WowProj',
                     'stsManifestId': '123-456-789',
                     'createdAt': '2020-05-17T00:00:00Z',
                     'numberOfSamples': 1,
                     'user': {'email': 'test_user_requester@sanger.ac.uk',
                              'name': 'test_user_requester',
                              'organisation': 'Sanger Institute',
                              'roles': []}}
                    ]
        self.assertEqual(expected, response.json)

    @responses.activate
    @patch('main.manifest_utils.get_ncbi_data')
    def test_fill_manifest(self, get_ncbi_data):
        mock_response_from_sts = {
            'data': {
                'list': [{
                    'sample_rackid': '1234',
                    'sample_tubeid': '5678'}]}
        }
        responses.add(responses.POST, os.getenv('STS_URL', '') + '/samples',
                      json=mock_response_from_sts, status=200)

        mock_response_from_sts_details = {
            'data': {
                'specimen_specimen_id': 'SAN1234567',
                'sample_biosample_accession': 'SAMEA7701758',
                'sample_relationship': '',
                'gal_name': 'UNIVERSITY OF OXFORD',
                'sample_col_date': '2020-07-24',
                'location_location': 'United Kingdom | Berkshire | Wytham woods',
                'location_lat': '51.77',
                'location_long': '-1.339',
                'location_habitat': 'On thistle | Grassland',
                'location_depth': '',
                'location_elevation': '150',
                'sample_voucherid': 'NOT_APPLICABLE',
                'sample_symbiont': 'TARGET',
                'ext_id_value_GAL_SAMPLE_ID': 'Ox000701',
                'ext_id_value_COL_SAMPLE_ID': 'COL1',
                'person_fullname_COLLECT': 'Collector 1',
                'person_fullname_IDENTIFY': 'Identifier 1',
                'institution_name_COLLECT': 'University of Oxford',
                'institution_name_IDENTIFY': 'University of Oxford',
                'specimen_bio_specimen_id': 'SAMEA7701562',
                'location_grid_reference': 'GB123456',
                'cmethod_method': 'Grasped',
                'imethod_method': 'Looking',
                'sample_specimen_risk': 'Y',
                'person_fullname_PRESERVE': 'A Preserver',
                'institution_name_PRESERVE': 'Sample Preservation Society',
                'papproach_approach': 'solution',
                'psolution_solution': 'ethanol',
                'sample_pre_elapsed': '1',
                'sample_pre_date': '1/1/2020',
                'tissue_size_size': 'NOT_APPLICABLE',
                'sample_tremoved': 'Y',
                'sample_bplateid': 'PLATE1',
                'sample_btubeid': 'TUBE1',
                'sample_bplate_pre': 'Jelly',
                'specimen_purpose_purpose': 'DNA_BARCODING_ONLY',
                'hazard_group_level': 'HG1',
                'sample_reg_compliance': 'Y',
                'sample_original_collection_date': '1/1/2021',
                'sample_original_geographic_location': 'United Kingdom | Cambridge',
                'sample_barcode_hub': 'London'
            }
        }
        responses.add(responses.GET, os.getenv('STS_URL', '') + '/samples/detail',
                      json=mock_response_from_sts_details, status=200)

        get_ncbi_data.return_value = {63445: {
            'TaxId': '6344',
            'ScientificName': 'Arenicola marina symbiont',
            'OtherNames': {
                'Anamorph': [],
                'CommonName': ['rock worm'],
                'Misnomer': [],
                'Inpart': [],
                'GenbankAnamorph': [],
                'Misspelling': [],
                'Includes': [],
                'EquivalentName': [],
                'Name': [{
                    'ClassCDE': 'authority',
                    'DispName': 'Arenicola marina (Linnaeus, 1758)'
                }, {
                    'ClassCDE': 'authority',
                    'DispName': 'Lumbricus marinus Linnaeus, 1758'
                }],
                'Synonym': ['Lumbricus marinus'],
                'GenbankSynonym': [],
                'Teleomorph': [],
                'Acronym': [],
                'GenbankCommonName': 'lugworm'},
            'ParentTaxId': '6343',
            'Rank': 'species',
            'Division': 'Invertebrates',
            'GeneticCode': {'GCId': '1', 'GCName': 'Standard'},
            'MitoGeneticCode': {'MGCId': '5', 'MGCName': 'Invertebrate Mitochondrial'},
            'Lineage': 'cellular organisms; Eukaryota; Opisthokonta; Metazoa; Eumetazoa; Bilateria; Protostomia; Spiralia; Lophotrochozoa; Annelida; Polychaeta; Sedentaria; Scolecida; Arenicolidae; Arenicola',  # noqa
            'LineageEx': [
                {'TaxId': '131567', 'ScientificName': 'cellular organisms', 'Rank': 'no rank'},
                {'TaxId': '2759', 'ScientificName': 'Eukaryota', 'Rank': 'superkingdom'},
                {'TaxId': '33154', 'ScientificName': 'Opisthokonta', 'Rank': 'clade'},
                {'TaxId': '33208', 'ScientificName': 'Metazoa', 'Rank': 'kingdom'},
                {'TaxId': '6072', 'ScientificName': 'Eumetazoa', 'Rank': 'clade'},
                {'TaxId': '33213', 'ScientificName': 'Bilateria', 'Rank': 'clade'},
                {'TaxId': '33317', 'ScientificName': 'Protostomia', 'Rank': 'clade'},
                {'TaxId': '2697495', 'ScientificName': 'Spiralia', 'Rank': 'clade'},
                {'TaxId': '1206795', 'ScientificName': 'Lophotrochozoa', 'Rank': 'clade'},
                {'TaxId': '6340', 'ScientificName': 'Annelida', 'Rank': 'phylum'},
                {'TaxId': '6341', 'ScientificName': 'Polychaeta', 'Rank': 'class'},
                {'TaxId': '105389', 'ScientificName': 'Sedentaria', 'Rank': 'subclass'},
                {'TaxId': '105387', 'ScientificName': 'Scolecida', 'Rank': 'infraclass'},
                {'TaxId': '42115', 'ScientificName': 'Arenicolidae', 'Rank': 'family'},
                {'TaxId': '6343', 'ScientificName': 'Arenicola', 'Rank': 'genus'}],
            'CreateDate': '1995/02/27 09: 24: 00',
            'UpdateDate': '2020/11/03 16: 20: 42',
            'PubDate': '1996/01/18 00: 00: 00'}
        }

        # Correct, symbiont-only JSON
        body = {'samples': [{
            'row': 1,
            'SPECIMEN_ID': 'SAN1234567',
            'TAXON_ID': 63445,
            'SCIENTIFIC_NAME': 'Arenicola marina symbiont',
            'LIFESTAGE': 'ADULT',
            'SEX': 'FEMALE',
            'ORGANISM_PART': 'MUSCLE',
            'SYMBIONT': 'SYMBIONT',
            'GAL': 'NATURAL HISTORY MUSEUM'}  # Can override GAL here
        ]}
        response = self.client.open(
            '/api/v1/manifests',
            method='POST',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        response = self.client.open(
            '/api/v1/manifests/1/fill',
            method='PATCH',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        expected = {'manifestId': 1,
                    'submissionStatus': None,
                    'projectName': 'ToL',  # Default - not given in body
                    'stsManifestId': None,  # Default - not given in body
                    'samples': [
                        {'row': 1,
                         'SPECIMEN_ID': 'SAN1234567',
                         'TAXON_ID': 63445,
                         'SCIENTIFIC_NAME': 'Arenicola marina symbiont',
                         'GENUS': 'Arenicola',
                         'FAMILY': 'Arenicolidae',
                         'ORDER_OR_GROUP': None,
                         'COMMON_NAME': None,
                         'LIFESTAGE': 'ADULT',
                         'SEX': 'FEMALE',
                         'ORGANISM_PART': 'MUSCLE',
                         'GAL': 'NATURAL HISTORY MUSEUM',
                         'GAL_SAMPLE_ID': 'Ox000701',
                         'COLLECTED_BY': 'Collector 1',
                         'COLLECTOR_AFFILIATION': 'University of Oxford',
                         'DATE_OF_COLLECTION': '2020-07-24',
                         'COLLECTION_LOCATION': 'United Kingdom | Berkshire | Wytham woods',
                         'DECIMAL_LATITUDE': '51.77',
                         'DECIMAL_LONGITUDE': '-1.339',
                         'HABITAT': 'On thistle | Grassland',
                         'IDENTIFIED_BY': 'Identifier 1',
                         'IDENTIFIER_AFFILIATION': 'University of Oxford',
                         'VOUCHER_ID': 'NOT_APPLICABLE',
                         'OTHER_INFORMATION': None,
                         'ELEVATION': '150',
                         'DEPTH': None,
                         'RELATIONSHIP': None,
                         'SYMBIONT': 'SYMBIONT',
                         'CULTURE_OR_STRAIN_ID': None,
                         'SERIES': None,
                         'RACK_OR_PLATE_ID': None,
                         'TUBE_OR_WELL_ID': None,
                         'TAXON_REMARKS': None,
                         'INFRASPECIFIC_EPITHET': None,
                         'COLLECTOR_SAMPLE_ID': 'COL1',
                         'GRID_REFERENCE': 'GB123456',
                         'TIME_OF_COLLECTION': None,
                         'DESCRIPTION_OF_COLLECTION_METHOD': 'Grasped',
                         'DIFFICULT_OR_HIGH_PRIORITY_SAMPLE': None,
                         'IDENTIFIED_HOW': 'Looking',
                         'SPECIMEN_ID_RISK': 'Y',
                         'PRESERVED_BY': 'A Preserver',
                         'PRESERVER_AFFILIATION': 'Sample Preservation Society',
                         'PRESERVATION_APPROACH': 'solution',
                         'PRESERVATIVE_SOLUTION': 'ethanol',
                         'TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION': '1',
                         'DATE_OF_PRESERVATION': '1/1/2020',
                         'SIZE_OF_TISSUE_IN_TUBE': 'NOT_APPLICABLE',
                         'TISSUE_REMOVED_FOR_BARCODING': 'Y',
                         'PLATE_ID_FOR_BARCODING': 'PLATE1',
                         'TUBE_OR_WELL_ID_FOR_BARCODING': 'TUBE1',
                         'TISSUE_FOR_BARCODING': None,
                         'BARCODE_PLATE_PRESERVATIVE': 'Jelly',
                         'PURPOSE_OF_SPECIMEN': 'DNA_BARCODING_ONLY',
                         'HAZARD_GROUP': 'HG1',
                         'REGULATORY_COMPLIANCE': 'Y',
                         'ORIGINAL_COLLECTION_DATE': '1/1/2021',
                         'ORIGINAL_GEOGRAPHIC_LOCATION': 'United Kingdom | Cambridge',
                         'BARCODE_HUB': 'London',
                         'tolId': None,
                         'biosampleAccession': None,
                         'sraAccession': None,
                         'submissionAccession': None,
                         'submissionError': None,
                         'sampleSameAs': None,
                         'sampleDerivedFrom': None,
                         'sampleSymbiontOf': None}
                    ]}
        self.assertEqual(expected, response.json)

    @responses.activate
    @patch('main.manifest_utils.get_ncbi_data')
    def test_fill_manifest_sample_not_in_sts(self, get_ncbi_data):
        mock_response_from_sts = {}
        responses.add(responses.POST, os.getenv('STS_URL', '') + '/samples',
                      json=mock_response_from_sts, status=400)

        get_ncbi_data.return_value = {63445: {
            'TaxId': '6344',
            'ScientificName': 'Arenicola marina symbiont',
            'OtherNames': {
                'Anamorph': [],
                'CommonName': ['rock worm'],
                'Misnomer': [],
                'Inpart': [],
                'GenbankAnamorph': [],
                'Misspelling': [],
                'Includes': [],
                'EquivalentName': [],
                'Name': [{
                    'ClassCDE': 'authority',
                    'DispName': 'Arenicola marina (Linnaeus, 1758)'
                }, {
                    'ClassCDE': 'authority',
                    'DispName': 'Lumbricus marinus Linnaeus, 1758'
                }],
                'Synonym': ['Lumbricus marinus'],
                'GenbankSynonym': [],
                'Teleomorph': [],
                'Acronym': [],
                'GenbankCommonName': 'lugworm'},
            'ParentTaxId': '6343',
            'Rank': 'species',
            'Division': 'Invertebrates',
            'GeneticCode': {'GCId': '1', 'GCName': 'Standard'},
            'MitoGeneticCode': {'MGCId': '5', 'MGCName': 'Invertebrate Mitochondrial'},
            'Lineage': 'cellular organisms; Eukaryota; Opisthokonta; Metazoa; Eumetazoa; Bilateria; Protostomia; Spiralia; Lophotrochozoa; Annelida; Polychaeta; Sedentaria; Scolecida; Arenicolidae; Arenicola',  # noqa
            'LineageEx': [
                {'TaxId': '131567', 'ScientificName': 'cellular organisms', 'Rank': 'no rank'},
                {'TaxId': '2759', 'ScientificName': 'Eukaryota', 'Rank': 'superkingdom'},
                {'TaxId': '33154', 'ScientificName': 'Opisthokonta', 'Rank': 'clade'},
                {'TaxId': '33208', 'ScientificName': 'Metazoa', 'Rank': 'kingdom'},
                {'TaxId': '6072', 'ScientificName': 'Eumetazoa', 'Rank': 'clade'},
                {'TaxId': '33213', 'ScientificName': 'Bilateria', 'Rank': 'clade'},
                {'TaxId': '33317', 'ScientificName': 'Protostomia', 'Rank': 'clade'},
                {'TaxId': '2697495', 'ScientificName': 'Spiralia', 'Rank': 'clade'},
                {'TaxId': '1206795', 'ScientificName': 'Lophotrochozoa', 'Rank': 'clade'},
                {'TaxId': '6340', 'ScientificName': 'Annelida', 'Rank': 'phylum'},
                {'TaxId': '6341', 'ScientificName': 'Polychaeta', 'Rank': 'class'},
                {'TaxId': '105389', 'ScientificName': 'Sedentaria', 'Rank': 'subclass'},
                {'TaxId': '105387', 'ScientificName': 'Scolecida', 'Rank': 'infraclass'},
                {'TaxId': '42115', 'ScientificName': 'Arenicolidae', 'Rank': 'family'},
                {'TaxId': '6343', 'ScientificName': 'Arenicola', 'Rank': 'genus'}],
            'CreateDate': '1995/02/27 09: 24: 00',
            'UpdateDate': '2020/11/03 16: 20: 42',
            'PubDate': '1996/01/18 00: 00: 00'}
        }

        # Correct, symbiont-only JSON
        body = {'samples': [{
            'row': 1,
            'SPECIMEN_ID': 'SAN1234567',
            'TAXON_ID': 63445,
            'SCIENTIFIC_NAME': 'Arenicola marina symbiont',
            'LIFESTAGE': 'ADULT',
            'SEX': 'FEMALE',
            'ORGANISM_PART': 'MUSCLE',
            'SYMBIONT': 'SYMBIONT'}
        ]}
        response = self.client.open(
            '/api/v1/manifests',
            method='POST',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        response = self.client.open(
            '/api/v1/manifests/1/fill',
            method='PATCH',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert404(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    @responses.activate
    @patch('main.manifest_utils.get_ncbi_data')
    def test_fill_manifest_sample_not_in_ncbi(self, get_ncbi_data):
        mock_response_from_sts = {
            'data': {
                'list': [{
                    'sample_rackid': '1234',
                    'sample_tubeid': '5678'}]}
        }
        responses.add(responses.POST, os.getenv('STS_URL', '') + '/samples',
                      json=mock_response_from_sts, status=200)

        mock_response_from_sts_details = {
            'data': {
                'specimen_specimen_id': 'SAN1234567',
                'sample_biosample_accession': 'SAMEA7701758',
                'sample_relationship': '',
                'gal_name': 'UNIVERSITY OF OXFORD',
                'sample_col_date': '2020-07-24',
                'location_location': 'United Kingdom | Berkshire | Wytham woods',
                'location_lat': '51.77',
                'location_long': '-1.339',
                'location_habitat': 'On thistle | Grassland',
                'location_depth': '',
                'location_elevation': '150',
                'sample_voucherid': 'NOT_APPLICABLE',
                'sample_symbiont': 'TARGET',
                'ext_id_value_GAL_SAMPLE_ID': 'Ox000701',
                'ext_id_value_COL_SAMPLE_ID': 'COL1',
                'person_fullname_COLLECT': 'Collector 1',
                'person_fullname_IDENTIFY': 'Identifier 1',
                'institution_name_COLLECT': 'University of Oxford',
                'institution_name_IDENTIFY': 'University of Oxford',
                'specimen_bio_specimen_id': 'SAMEA7701562',
                'location_grid_reference': 'GB123456',
                'cmethod_method': 'Grasped',
                'imethod_method': 'Looking',
                'sample_specimen_risk': 'Y',
                'person_fullname_PRESERVE': 'A Preserver',
                'institution_name_PRESERVE': 'Sample Preservation Society',
                'papproach_approach': 'solution',
                'psolution_solution': 'ethanol',
                'sample_pre_elapsed': '1',
                'sample_pre_date': '1/1/2020',
                'tissue_size_size': 'NOT_APPLICABLE',
                'sample_tremoved': 'Y',
                'sample_bplateid': 'PLATE1',
                'sample_btubeid': 'TUBE1',
                'sample_bplate_pre': 'Jelly',
                'specimen_purpose_purpose': 'DNA_BARCODING_ONLY',
                'hazard_group_level': 'HG1',
                'sample_reg_compliance': 'Y',
                'sample_original_collection_date': '1/1/2021',
                'sample_original_geographic_location': 'United Kingdom | Cambridge',
                'sample_barcode_hub': 'London'
            }
        }
        responses.add(responses.GET, os.getenv('STS_URL', '') + '/samples/detail',
                      json=mock_response_from_sts_details, status=200)

        get_ncbi_data.return_value = {}

        # Correct, symbiont-only JSON
        body = {'samples': [{
            'row': 1,
            'SPECIMEN_ID': 'SAN1234567',
            'TAXON_ID': 63445,
            'SCIENTIFIC_NAME': 'Arenicola marina symbiont',
            'LIFESTAGE': 'ADULT',
            'SEX': 'FEMALE',
            'ORGANISM_PART': 'MUSCLE',
            'SYMBIONT': 'SYMBIONT'}
        ]}
        response = self.client.open(
            '/api/v1/manifests',
            method='POST',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        response = self.client.open(
            '/api/v1/manifests/1/fill',
            method='PATCH',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert404(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    @responses.activate
    @patch('main.manifest_utils.get_ncbi_data')
    def test_fill_manifest_sample_not_in_sts_2(self, get_ncbi_data):
        mock_response_from_sts = {'data': {'list': []}}
        responses.add(responses.POST, os.getenv('STS_URL', '') + '/samples',
                      json=mock_response_from_sts, status=200)

        get_ncbi_data.return_value = {63445: {
            'TaxId': '6344',
            'ScientificName': 'Arenicola marina symbiont',
            'OtherNames': {
                'Anamorph': [],
                'CommonName': ['rock worm'],
                'Misnomer': [],
                'Inpart': [],
                'GenbankAnamorph': [],
                'Misspelling': [],
                'Includes': [],
                'EquivalentName': [],
                'Name': [{
                    'ClassCDE': 'authority',
                    'DispName': 'Arenicola marina (Linnaeus, 1758)'
                }, {
                    'ClassCDE': 'authority',
                    'DispName': 'Lumbricus marinus Linnaeus, 1758'
                }],
                'Synonym': ['Lumbricus marinus'],
                'GenbankSynonym': [],
                'Teleomorph': [],
                'Acronym': [],
                'GenbankCommonName': 'lugworm'},
            'ParentTaxId': '6343',
            'Rank': 'species',
            'Division': 'Invertebrates',
            'GeneticCode': {'GCId': '1', 'GCName': 'Standard'},
            'MitoGeneticCode': {'MGCId': '5', 'MGCName': 'Invertebrate Mitochondrial'},
            'Lineage': 'cellular organisms; Eukaryota; Opisthokonta; Metazoa; Eumetazoa; Bilateria; Protostomia; Spiralia; Lophotrochozoa; Annelida; Polychaeta; Sedentaria; Scolecida; Arenicolidae; Arenicola',  # noqa
            'LineageEx': [
                {'TaxId': '131567', 'ScientificName': 'cellular organisms', 'Rank': 'no rank'},
                {'TaxId': '2759', 'ScientificName': 'Eukaryota', 'Rank': 'superkingdom'},
                {'TaxId': '33154', 'ScientificName': 'Opisthokonta', 'Rank': 'clade'},
                {'TaxId': '33208', 'ScientificName': 'Metazoa', 'Rank': 'kingdom'},
                {'TaxId': '6072', 'ScientificName': 'Eumetazoa', 'Rank': 'clade'},
                {'TaxId': '33213', 'ScientificName': 'Bilateria', 'Rank': 'clade'},
                {'TaxId': '33317', 'ScientificName': 'Protostomia', 'Rank': 'clade'},
                {'TaxId': '2697495', 'ScientificName': 'Spiralia', 'Rank': 'clade'},
                {'TaxId': '1206795', 'ScientificName': 'Lophotrochozoa', 'Rank': 'clade'},
                {'TaxId': '6340', 'ScientificName': 'Annelida', 'Rank': 'phylum'},
                {'TaxId': '6341', 'ScientificName': 'Polychaeta', 'Rank': 'class'},
                {'TaxId': '105389', 'ScientificName': 'Sedentaria', 'Rank': 'subclass'},
                {'TaxId': '105387', 'ScientificName': 'Scolecida', 'Rank': 'infraclass'},
                {'TaxId': '42115', 'ScientificName': 'Arenicolidae', 'Rank': 'family'},
                {'TaxId': '6343', 'ScientificName': 'Arenicola', 'Rank': 'genus'}],
            'CreateDate': '1995/02/27 09: 24: 00',
            'UpdateDate': '2020/11/03 16: 20: 42',
            'PubDate': '1996/01/18 00: 00: 00'}
        }

        # Correct, symbiont-only JSON
        body = {'samples': [{
            'row': 1,
            'SPECIMEN_ID': 'SAN1234567',
            'TAXON_ID': 63445,
            'SCIENTIFIC_NAME': 'Arenicola marina symbiont',
            'LIFESTAGE': 'ADULT',
            'SEX': 'FEMALE',
            'ORGANISM_PART': 'MUSCLE',
            'SYMBIONT': 'SYMBIONT'}
        ]}
        response = self.client.open(
            '/api/v1/manifests',
            method='POST',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        response = self.client.open(
            '/api/v1/manifests/1/fill',
            method='PATCH',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert404(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    @responses.activate
    @patch('main.manifest_utils.get_ncbi_data')
    def test_validate_manifest_json(self, get_ncbi_data):
        mock_response_from_ena = {'taxId': '6344',
                                  'scientificName': 'Arenicola marina',
                                  'commonName': 'lugworm',
                                  'formalName': 'true',
                                  'rank': 'species',
                                  'division': 'INV',
                                  'lineage': '',
                                  'geneticCode': '1',
                                  'mitochondrialGeneticCode': '5',
                                  'submittable': 'true'}
        responses.add(responses.GET, 'https://www.ebi.ac.uk/ena/taxonomy/rest/tax-id/6344',
                      json=mock_response_from_ena, status=200)
        mock_response_from_tolid = [{'taxonomyId': '6344',
                                     'scientificName': 'Arenicola marina',
                                     'commonName': 'lugworm',
                                     'family': 'Arenicolidae',
                                     'genus': 'Arenicola',
                                     'order': 'None'}]
        responses.add(responses.GET, os.getenv('TOLID_URL', '') + '/species/6344',
                      json=mock_response_from_tolid, status=200)

        mock_response_from_tolid_specimen = [{
            'specimenId': 'SAN1234567',
            'tolIds': [{
                'species': {
                    'commonName': 'lugworm',
                    'currentHighestTolidNumber': 2,
                    'family': 'Arenicolidae',
                    'genus': 'Arenicola',
                    'kingdom': 'Metazoa',
                    'order': 'Capitellida',
                    'phylum': 'Annelida',
                    'prefix': 'wuAreMari',
                    'scientificName': 'Arenicola marina',
                    'taxaClass': 'Polychaeta',
                    'taxonomyId': 6344
                },
                'tolId': 'wuAreMari1'
            }]
        }]
        responses.add(responses.GET, os.getenv('TOLID_URL', '') + '/specimens/SAN1234567',
                      json=mock_response_from_tolid_specimen, status=200)

        mock_response_from_sts = {}  # Only interested in status codes
        responses.add(responses.GET, os.getenv('STS_URL', '') + '/samples/detail',
                      json=mock_response_from_sts, status=400)

        get_ncbi_data.return_value = {6344: {
            'TaxId': '6344',
            'ScientificName': 'Arenicola marina',
            'OtherNames': {
                'Anamorph': [],
                'CommonName': ['rock worm'],
                'Misnomer': [],
                'Inpart': [],
                'GenbankAnamorph': [],
                'Misspelling': [],
                'Includes': [],
                'EquivalentName': [],
                'Name': [{
                    'ClassCDE': 'authority',
                    'DispName': 'Arenicola marina (Linnaeus, 1758)'
                }, {
                    'ClassCDE': 'authority',
                    'DispName': 'Lumbricus marinus Linnaeus, 1758'
                }],
                'Synonym': ['Lumbricus marinus'],
                'GenbankSynonym': [],
                'Teleomorph': [],
                'Acronym': [],
                'GenbankCommonName': 'lugworm'},
            'ParentTaxId': '6343',
            'Rank': 'species',
            'Division': 'Invertebrates',
            'GeneticCode': {'GCId': '1', 'GCName': 'Standard'},
            'MitoGeneticCode': {'MGCId': '5', 'MGCName': 'Invertebrate Mitochondrial'},
            'Lineage': 'cellular organisms; Eukaryota; Opisthokonta; Metazoa; Eumetazoa; Bilateria; Protostomia; Spiralia; Lophotrochozoa; Annelida; Polychaeta; Sedentaria; Scolecida; Arenicolidae; Arenicola',  # noqa
            'LineageEx': [
                {'TaxId': '131567', 'ScientificName': 'cellular organisms', 'Rank': 'no rank'},
                {'TaxId': '2759', 'ScientificName': 'Eukaryota', 'Rank': 'superkingdom'},
                {'TaxId': '33154', 'ScientificName': 'Opisthokonta', 'Rank': 'clade'},
                {'TaxId': '33208', 'ScientificName': 'Metazoa', 'Rank': 'kingdom'},
                {'TaxId': '6072', 'ScientificName': 'Eumetazoa', 'Rank': 'clade'},
                {'TaxId': '33213', 'ScientificName': 'Bilateria', 'Rank': 'clade'},
                {'TaxId': '33317', 'ScientificName': 'Protostomia', 'Rank': 'clade'},
                {'TaxId': '2697495', 'ScientificName': 'Spiralia', 'Rank': 'clade'},
                {'TaxId': '1206795', 'ScientificName': 'Lophotrochozoa', 'Rank': 'clade'},
                {'TaxId': '6340', 'ScientificName': 'Annelida', 'Rank': 'phylum'},
                {'TaxId': '6341', 'ScientificName': 'Polychaeta', 'Rank': 'class'},
                {'TaxId': '105389', 'ScientificName': 'Sedentaria', 'Rank': 'subclass'},
                {'TaxId': '105387', 'ScientificName': 'Scolecida', 'Rank': 'infraclass'},
                {'TaxId': '42115', 'ScientificName': 'Arenicolidae', 'Rank': 'family'},
                {'TaxId': '6343', 'ScientificName': 'Arenicola', 'Rank': 'genus'}],
            'CreateDate': '1995/02/27 09: 24: 00',
            'UpdateDate': '2020/11/03 16: 20: 42',
            'PubDate': '1996/01/18 00: 00: 00'}
        }

        body = {'samples': [{
            'row': 1,
            'SPECIMEN_ID': 'SAN1234567',
            'TAXON_ID': 6344,
            'SCIENTIFIC_NAME': 'Arenicola marina',
            'GENUS': 'Arenicola',
            'FAMILY': 'Arenicolidae',
            'ORDER_OR_GROUP': 'Scolecida',
            'COMMON_NAME': 'lugworm',
            'LIFESTAGE': 'ADULT',
            'SEX': 'FEMALE',
            'ORGANISM_PART': 'MUSCLE',
            'GAL': 'SANGER INSTITUTE',
            'GAL_SAMPLE_ID': 'SAN0000100',
            'COLLECTED_BY': 'ALEX COLLECTOR',
            'COLLECTOR_AFFILIATION': 'THE COLLECTOR INSTITUTE',
            'DATE_OF_COLLECTION': '2020-09-01',
            'COLLECTION_LOCATION': 'UNITED KINGDOM | DARK FOREST',
            'DECIMAL_LATITUDE': '+50.12345678',
            'DECIMAL_LONGITUDE': '-1.98765432',
            'HABITAT': 'Woodland',
            'IDENTIFIED_BY': 'JO IDENTIFIER',
            'IDENTIFIER_AFFILIATION': 'THE IDENTIFIER INSTITUTE',
            'VOUCHER_ID': ''}
        ]}

        # Submit the manifest
        response = self.client.open(
            '/api/v1/manifests',
            method='POST',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # No authorisation token given
        body = []
        response = self.client.open(
            '/api/v1/manifests/1/validate',
            method='GET',
            json=body)
        self.assert401(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Invalid authorisation token given
        body = []
        response = self.client.open(
            '/api/v1/manifests/1/validate',
            method='GET',
            headers={'api-key': '12345678'},
            json=body)
        self.assert401(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Incorrect manifest ID
        body = {}
        response = self.client.open(
            '/api/v1/manifests/2/validate',
            method='GET',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert404(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Not a submitter
        response = self.client.open(
            '/api/v1/manifests/1/validate',
            method='GET',
            headers={'api-key': self.user1.api_key},
            json=body)
        self.assert403(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Corect - should validate and return errors
        response = self.client.open(
            '/api/v1/manifests/1/validate',
            method='GET',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        expected = {'manifestId': 1,
                    'number_of_errors': 1,
                    'validations': [
                        {'row': 1,
                         'results': [
                             {'field': 'VOUCHER_ID',
                              'message': 'Must not be empty',
                              'severity': 'ERROR'}
                         ]}
                    ]}
        self.assertEqual(expected, response.json)

    @responses.activate
    @patch('main.manifest_utils.get_ncbi_data')
    def test_validate_manifest_json_unknown_taxon(self, get_ncbi_data):
        mock_response_from_ena = {'taxId': '32644',
                                  'scientificName': 'unidentified',
                                  'formalName': 'true',
                                  'rank': 'species',
                                  'division': 'UNK',
                                  'lineage': '',
                                  'geneticCode': '1',
                                  'mitochondrialGeneticCode': '5',
                                  'submittable': 'true'}
        responses.add(responses.GET, 'https://www.ebi.ac.uk/ena/taxonomy/rest/tax-id/32644',
                      json=mock_response_from_ena, status=200)
        mock_response_from_tolid = [{'taxonomyId': '32644',
                                     'scientificName': 'unidentified',
                                     'commonName': '',
                                     'family': '',
                                     'genus': '',
                                     'order': 'None'}]
        responses.add(responses.GET, os.getenv('TOLID_URL', '') + '/species/32644',
                      json=mock_response_from_tolid, status=200)

        mock_response_from_tolid_specimen = [{
            'specimenId': 'SAN1234567',
            'tolIds': [{
                'species': {
                    'commonName': '',
                    'currentHighestTolidNumber': 2,
                    'family': '',
                    'genus': '',
                    'kingdom': '',
                    'order': '',
                    'phylum': '',
                    'prefix': 'unUnkUnkn',
                    'scientificName': 'unidentified',
                    'taxaClass': '',
                    'taxonomyId': 32644
                },
                'tolId': 'unUnkUnkn1'
            }]
        }]
        responses.add(responses.GET, os.getenv('TOLID_URL', '') + '/specimens/SAN1234567',
                      json=mock_response_from_tolid_specimen, status=200)

        mock_response_from_sts = {}  # Only interested in status codes
        responses.add(responses.GET, os.getenv('STS_URL', '') + '/samples/detail',
                      json=mock_response_from_sts, status=400)

        get_ncbi_data.return_value = {32644: {
            'TaxId': '32644',
            'ScientificName': 'unidentified',
            'OtherNames': {
                'Anamorph': [],
                'Inpart': [],
                'Misnomer': [],
                'Synonym': [
                    'miscellaneous nucleic acid', 'none', 'not shown', 'not specified', 'other',
                    'sonstige nucleic acid', 'unclassified sequence', 'unidentified organism',
                    'unidentified root endophyte', 'unknown', 'unknown organism', 'unspecified'
                ],
                'GenbankSynonym': [],
                'Teleomorph': [],
                'Misspelling': [],
                'CommonName': [],
                'Name': [{'ClassCDE': 'misspelling', 'DispName': 'unknwon'}],
                'Acronym': [],
                'EquivalentName': [],
                'Includes': [],
                'GenbankAnamorph': []
            },
            'ParentTaxId': '12908',
            'Rank': 'species',
            'Division': 'Unassigned',
            'GeneticCode': {'GCId': '1', 'GCName': 'Standard'},
            'MitoGeneticCode': {'MGCId': '2', 'MGCName': 'Vertebrate Mitochondrial'},
            'Lineage': 'unclassified entries; unclassified sequences',
            'LineageEx': [
                {'TaxId': '2787823', 'ScientificName': 'unclassified entries', 'Rank': 'no rank'},
                {'TaxId': '12908', 'ScientificName': 'unclassified sequences', 'Rank': 'no rank'}
            ],
            'Properties': [{'PropName': 'pgcode', 'PropValueInt': '11'}],
            'CreateDate': '1995/02/27 09:24:00',
            'UpdateDate': '2019/01/28 09:36:50',
            'PubDate': '1993/04/27 01:00:00'
        }}

        body = {'samples': [{
            'row': 1,
            'SPECIMEN_ID': 'SAN1234567',
            'TAXON_ID': 32644,
            'SCIENTIFIC_NAME': 'unidentified',
            'GENUS': '',
            'FAMILY': '',
            'ORDER_OR_GROUP': '',
            'COMMON_NAME': '',
            'LIFESTAGE': 'ADULT',
            'SEX': 'FEMALE',
            'ORGANISM_PART': 'MUSCLE',
            'GAL': 'SANGER INSTITUTE',
            'GAL_SAMPLE_ID': 'SAN0000100',
            'COLLECTED_BY': 'ALEX COLLECTOR',
            'COLLECTOR_AFFILIATION': 'THE COLLECTOR INSTITUTE',
            'DATE_OF_COLLECTION': '2020-09-01',
            'COLLECTION_LOCATION': 'UNITED KINGDOM | DARK FOREST',
            'DECIMAL_LATITUDE': '+50.12345678',
            'DECIMAL_LONGITUDE': '-1.98765432',
            'HABITAT': 'Woodland',
            'IDENTIFIED_BY': 'JO IDENTIFIER',
            'IDENTIFIER_AFFILIATION': 'THE IDENTIFIER INSTITUTE',
            'VOUCHER_ID': 'voucher1',
            'public_name': 'TEST1'}
        ]}

        # Submit the manifest
        response = self.client.open(
            '/api/v1/manifests',
            method='POST',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # No authorisation token given
        body = []
        response = self.client.open(
            '/api/v1/manifests/1/validate',
            method='GET',
            json=body)
        self.assert401(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Invalid authorisation token given
        body = []
        response = self.client.open(
            '/api/v1/manifests/1/validate',
            method='GET',
            headers={'api-key': '12345678'},
            json=body)
        self.assert401(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Incorrect manifest ID
        body = {}
        response = self.client.open(
            '/api/v1/manifests/2/validate',
            method='GET',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert404(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Not a submitter
        response = self.client.open(
            '/api/v1/manifests/1/validate',
            method='GET',
            headers={'api-key': self.user1.api_key},
            json=body)
        self.assert403(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Corect - should validate and return errors
        response = self.client.open(
            '/api/v1/manifests/1/validate',
            method='GET',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        expected = {'manifestId': 1,
                    'number_of_errors': 0,
                    'validations': [
                        {'row': 1,
                         'results': []}
                    ]}
        self.assertEqual(expected, response.json)

    @responses.activate
    @patch('main.manifest_utils.get_ncbi_data')
    def test_submit_and_validate_manifest_json(self, get_ncbi_data):
        mock_response_from_ena = {'taxId': '6344',
                                  'scientificName': 'Arenicola marina',
                                  'commonName': 'lugworm',
                                  'formalName': 'true',
                                  'rank': 'species',
                                  'division': 'INV',
                                  'lineage': '',
                                  'geneticCode': '1',
                                  'mitochondrialGeneticCode': '5',
                                  'submittable': 'true'}
        responses.add(responses.GET, 'https://www.ebi.ac.uk/ena/taxonomy/rest/tax-id/6344',
                      json=mock_response_from_ena, status=200)
        mock_response_from_tolid = [{'taxonomyId': '6344',
                                     'scientificName': 'Arenicola marina',
                                     'commonName': 'lugworm',
                                     'family': 'Arenicolidae',
                                     'genus': 'Arenicola',
                                     'order': 'None'}]
        responses.add(responses.GET, os.getenv('TOLID_URL', '') + '/species/6344',
                      json=mock_response_from_tolid, status=200)

        mock_response_from_tolid_specimen = [{
            'specimenId': 'SAN1234567',
            'tolIds': [{
                'species': {
                    'commonName': 'lugworm',
                    'currentHighestTolidNumber': 2,
                    'family': 'Arenicolidae',
                    'genus': 'Arenicola',
                    'kingdom': 'Metazoa',
                    'order': 'Capitellida',
                    'phylum': 'Annelida',
                    'prefix': 'wuAreMari',
                    'scientificName': 'Arenicola marina',
                    'taxaClass': 'Polychaeta',
                    'taxonomyId': 6344
                },
                'tolId': 'wuAreMari1'
            }]
        }]
        responses.add(responses.GET, os.getenv('TOLID_URL', '') + '/specimens/SAN1234567',
                      json=mock_response_from_tolid_specimen, status=200)

        mock_response_from_sts = {}  # Only interested in status codes
        responses.add(responses.GET, os.getenv('STS_URL', '') + '/samples/detail',
                      json=mock_response_from_sts, status=400)

        get_ncbi_data.return_value = {6344: {
            'TaxId': '6344',
            'ScientificName': 'Arenicola marina',
            'OtherNames': {
                'Anamorph': [],
                'CommonName': ['rock worm'],
                'Misnomer': [],
                'Inpart': [],
                'GenbankAnamorph': [],
                'Misspelling': [],
                'Includes': [],
                'EquivalentName': [],
                'Name': [{
                    'ClassCDE': 'authority',
                    'DispName': 'Arenicola marina (Linnaeus, 1758)'
                }, {
                    'ClassCDE': 'authority',
                    'DispName': 'Lumbricus marinus Linnaeus, 1758'
                }],
                'Synonym': ['Lumbricus marinus'],
                'GenbankSynonym': [],
                'Teleomorph': [],
                'Acronym': [],
                'GenbankCommonName': 'lugworm'},
            'ParentTaxId': '6343',
            'Rank': 'species',
            'Division': 'Invertebrates',
            'GeneticCode': {'GCId': '1', 'GCName': 'Standard'},
            'MitoGeneticCode': {'MGCId': '5', 'MGCName': 'Invertebrate Mitochondrial'},
            'Lineage': 'cellular organisms; Eukaryota; Opisthokonta; Metazoa; Eumetazoa; Bilateria; Protostomia; Spiralia; Lophotrochozoa; Annelida; Polychaeta; Sedentaria; Scolecida; Arenicolidae; Arenicola',  # noqa
            'LineageEx': [
                {'TaxId': '131567', 'ScientificName': 'cellular organisms', 'Rank': 'no rank'},
                {'TaxId': '2759', 'ScientificName': 'Eukaryota', 'Rank': 'superkingdom'},
                {'TaxId': '33154', 'ScientificName': 'Opisthokonta', 'Rank': 'clade'},
                {'TaxId': '33208', 'ScientificName': 'Metazoa', 'Rank': 'kingdom'},
                {'TaxId': '6072', 'ScientificName': 'Eumetazoa', 'Rank': 'clade'},
                {'TaxId': '33213', 'ScientificName': 'Bilateria', 'Rank': 'clade'},
                {'TaxId': '33317', 'ScientificName': 'Protostomia', 'Rank': 'clade'},
                {'TaxId': '2697495', 'ScientificName': 'Spiralia', 'Rank': 'clade'},
                {'TaxId': '1206795', 'ScientificName': 'Lophotrochozoa', 'Rank': 'clade'},
                {'TaxId': '6340', 'ScientificName': 'Annelida', 'Rank': 'phylum'},
                {'TaxId': '6341', 'ScientificName': 'Polychaeta', 'Rank': 'class'},
                {'TaxId': '105389', 'ScientificName': 'Sedentaria', 'Rank': 'subclass'},
                {'TaxId': '105387', 'ScientificName': 'Scolecida', 'Rank': 'infraclass'},
                {'TaxId': '42115', 'ScientificName': 'Arenicolidae', 'Rank': 'family'},
                {'TaxId': '6343', 'ScientificName': 'Arenicola', 'Rank': 'genus'}],
            'CreateDate': '1995/02/27 09: 24: 00',
            'UpdateDate': '2020/11/03 16: 20: 42',
            'PubDate': '1996/01/18 00: 00: 00'}
        }

        # No authorisation token given
        body = []
        response = self.client.open(
            '/api/v1/manifests/validate',
            method='POST',
            json=body)
        self.assert401(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Invalid authorisation token given
        body = []
        response = self.client.open(
            '/api/v1/manifests/validate',
            method='POST',
            headers={'api-key': '12345678'},
            json=body)
        self.assert401(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Body empty
        body = {}
        response = self.client.open(
            '/api/v1/manifests/validate',
            method='POST',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert400(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        body = {'samples': [{
            'row': 1,
            'SPECIMEN_ID': 'SAN1234567',
            'TAXON_ID': 6344,
            'SCIENTIFIC_NAME': 'Arenicola marina',
            'GENUS': 'Arenicola',
            'FAMILY': 'Arenicolidae',
            'ORDER_OR_GROUP': 'Scolecida',
            'COMMON_NAME': 'lugworm',
            'LIFESTAGE': 'ADULT',
            'SEX': 'FEMALE',
            'ORGANISM_PART': 'MUSCLE',
            'GAL': 'SANGER INSTITUTE',
            'GAL_SAMPLE_ID': 'SAN0000100',
            'COLLECTED_BY': 'ALEX COLLECTOR',
            'COLLECTOR_AFFILIATION': 'THE COLLECTOR INSTITUTE',
            'DATE_OF_COLLECTION': '2020-09-01',
            'COLLECTION_LOCATION': 'UNITED KINGDOM | DARK FOREST',
            'DECIMAL_LATITUDE': '+50.12345678',
            'DECIMAL_LONGITUDE': '-1.98765432',
            'HABITAT': 'Woodland',
            'IDENTIFIED_BY': 'JO IDENTIFIER',
            'IDENTIFIER_AFFILIATION': 'THE IDENTIFIER INSTITUTE',
            'VOUCHER_ID': ''}
        ]}
        # Not a submitter
        response = self.client.open(
            '/api/v1/manifests/validate',
            method='POST',
            headers={'api-key': self.user1.api_key},
            json=body)
        self.assert403(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Correct, full JSON
        response = self.client.open(
            '/api/v1/manifests/validate',
            method='POST',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        expected = {'manifestId': 1,
                    'number_of_errors': 1,
                    'validations': [
                        {'row': 1,
                         'results': [
                             {'field': 'VOUCHER_ID',
                              'message': 'Must not be empty',
                              'severity': 'ERROR'}
                         ]}
                    ]}
        self.assertEqual(expected, response.json)

    @responses.activate
    def test_generate_ids(self):
        specimen = SubmissionsSpecimen()
        specimen.specimen_id = 'SAN1234567'
        specimen.biosample_accession = 'SAMEA12345678'
        db.session.add(specimen)
        db.session.commit()

        mock_response_from_ena = {'taxId': '6344',
                                  'scientificName': 'Arenicola marina',
                                  'commonName': 'lugworm',
                                  'formalName': 'true',
                                  'rank': 'species',
                                  'division': 'INV',
                                  'lineage': '',
                                  'geneticCode': '1',
                                  'mitochondrialGeneticCode': '5',
                                  'submittable': 'true'}
        responses.add(responses.GET, 'https://www.ebi.ac.uk/ena/taxonomy/rest/tax-id/6344',
                      json=mock_response_from_ena, status=200)
        mock_response_from_tolid = [{
            'species': {
                'commonName': 'lugworm',
                'family': 'Arenicolidae',
                'genus': 'Arenicola',
                'kingdom': 'Metazoa',
                'order': 'Capitellida',
                'phylum': 'Annelida',
                'prefix': 'wuAreMari',
                'scientificName': 'Arenicola marina',
                'taxaClass': 'Polychaeta',
                'taxonomyId': 6344
            },
            'specimen': {
                'specimenId': 'SAN1234567'
            },
            'tolId': 'wuAreMari1'
        }]
        responses.add(responses.POST, os.getenv('TOLID_URL', '') + '/tol-ids',
                      json=mock_response_from_tolid, status=200)

        body = {'samples': [{
            'row': 1,
            'SPECIMEN_ID': 'SAN1234567',
            'TAXON_ID': 6344,
            'SCIENTIFIC_NAME': 'Arenicola marina',
            'GENUS': 'Arenicola',
            'FAMILY': 'Arenicolidae',
            'ORDER_OR_GROUP': 'Scolecida',
            'COMMON_NAME': 'lugworm',
            'LIFESTAGE': 'ADULT',
            'SEX': 'FEMALE',
            'ORGANISM_PART': 'MUSCLE',
            'GAL': 'SANGER INSTITUTE',
            'GAL_SAMPLE_ID': 'SAN0000100',
            'COLLECTED_BY': 'ALEX COLLECTOR',
            'COLLECTOR_AFFILIATION': 'THE COLLECTOR INSTITUTE',
            'DATE_OF_COLLECTION': '2020-09-01',
            'COLLECTION_LOCATION': 'UNITED KINGDOM | DARK FOREST',
            'DECIMAL_LATITUDE': '+50.12345678',
            'DECIMAL_LONGITUDE': '-1.98765432',
            'HABITAT': 'Woodland',
            'IDENTIFIED_BY': 'JO IDENTIFIER',
            'IDENTIFIER_AFFILIATION': 'THE IDENTIFIER INSTITUTE',
            'VOUCHER_ID': 'voucher1'}
        ]}

        # Submit the manifest
        response = self.client.open(
            '/api/v1/manifests',
            method='POST',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        manifest = db.session.query(SubmissionsManifest) \
            .filter(SubmissionsManifest.manifest_id == 1) \
            .one_or_none()
        mock_response_from_ena = '<?xml version="1.0" encoding="UTF-8"?><?xml-stylesheet type="text/xsl" href="receipt.xsl"?><RECEIPT receiptDate="2021-04-07T12:47:39.998+01:00" submissionFile="tmphz9luulrsubmission_3.xml" success="true"><SAMPLE accession="ERS6206028" alias="' + str(manifest.samples[0].sample_id) + '" status="PRIVATE"><EXT_ID accession="SAMEA8521239" type="biosample"/></SAMPLE><SUBMISSION accession="ERA3819349" alias="SUBMISSION-07-04-2021-12:47:36:825"/><ACTIONS>ADD</ACTIONS></RECEIPT>'  # noqa
        responses.add(responses.POST, os.getenv('ENA_URL', '') + '/ena/submit/drop-box/submit/',
                      body=mock_response_from_ena, status=200)

        # No authorisation token given
        body = []
        response = self.client.open(
            '/api/v1/manifests/1/generate',
            method='PATCH',
            json=body)
        self.assert401(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Invalid authorisation token given
        body = []
        response = self.client.open(
            '/api/v1/manifests/1/generate',
            method='PATCH',
            headers={'api-key': '12345678'},
            json=body)
        self.assert401(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Incorrect manifest ID
        body = {}
        response = self.client.open(
            '/api/v1/manifests/2/generate',
            method='PATCH',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert404(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Not a submitter
        response = self.client.open(
            '/api/v1/manifests/1/generate',
            method='PATCH',
            headers={'api-key': self.user1.api_key},
            json=body)
        self.assert403(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Corect - should validate and return errors
        response = self.client.open(
            '/api/v1/manifests/1/generate',
            method='PATCH',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        expected = {'manifestId': 1,
                    'submissionStatus': True,
                    'projectName': 'ToL',
                    'stsManifestId': None,
                    'samples': [{
                        'row': 1,
                        'SPECIMEN_ID': 'SAN1234567',
                        'TAXON_ID': 6344,
                        'SCIENTIFIC_NAME': 'Arenicola marina',
                        'GENUS': 'Arenicola',
                        'FAMILY': 'Arenicolidae',
                        'ORDER_OR_GROUP': 'Scolecida',
                        'COMMON_NAME': 'lugworm',
                        'LIFESTAGE': 'ADULT',
                        'SEX': 'FEMALE',
                        'ORGANISM_PART': 'MUSCLE',
                        'GAL': 'SANGER INSTITUTE',
                        'GAL_SAMPLE_ID': 'SAN0000100',
                        'COLLECTED_BY': 'ALEX COLLECTOR',
                        'COLLECTOR_AFFILIATION': 'THE COLLECTOR INSTITUTE',
                        'DATE_OF_COLLECTION': '2020-09-01',
                        'COLLECTION_LOCATION': 'UNITED KINGDOM | DARK FOREST',
                        'DECIMAL_LATITUDE': '+50.12345678',
                        'DECIMAL_LONGITUDE': '-1.98765432',
                        'HABITAT': 'Woodland',
                        'IDENTIFIED_BY': 'JO IDENTIFIER',
                        'IDENTIFIER_AFFILIATION': 'THE IDENTIFIER INSTITUTE',
                        'VOUCHER_ID': 'voucher1',
                        'OTHER_INFORMATION': None,
                        'DEPTH': None,
                        'ELEVATION': None,
                        'RELATIONSHIP': None,
                        'SYMBIONT': None,
                        'CULTURE_OR_STRAIN_ID': None,
                        'SERIES': None,
                        'RACK_OR_PLATE_ID': None,
                        'TUBE_OR_WELL_ID': None,
                        'TAXON_REMARKS': None,
                        'INFRASPECIFIC_EPITHET': None,
                        'COLLECTOR_SAMPLE_ID': None,
                        'GRID_REFERENCE': None,
                        'TIME_OF_COLLECTION': None,
                        'DESCRIPTION_OF_COLLECTION_METHOD': None,
                        'DIFFICULT_OR_HIGH_PRIORITY_SAMPLE': None,
                        'IDENTIFIED_HOW': None,
                        'SPECIMEN_ID_RISK': None,
                        'PRESERVED_BY': None,
                        'PRESERVER_AFFILIATION': None,
                        'PRESERVATION_APPROACH': None,
                        'PRESERVATIVE_SOLUTION': None,
                        'TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION': None,
                        'DATE_OF_PRESERVATION': None,
                        'SIZE_OF_TISSUE_IN_TUBE': None,
                        'TISSUE_REMOVED_FOR_BARCODING': None,
                        'PLATE_ID_FOR_BARCODING': None,
                        'TUBE_OR_WELL_ID_FOR_BARCODING': None,
                        'TISSUE_FOR_BARCODING': None,
                        'BARCODE_PLATE_PRESERVATIVE': None,
                        'PURPOSE_OF_SPECIMEN': None,
                        'HAZARD_GROUP': None,
                        'REGULATORY_COMPLIANCE': None,
                        'ORIGINAL_COLLECTION_DATE': None,
                        'ORIGINAL_GEOGRAPHIC_LOCATION': None,
                        'BARCODE_HUB': None,
                        'tolId': 'wuAreMari1',
                        'biosampleAccession': 'SAMEA8521239',
                        'sraAccession': 'ERS6206028',
                        'submissionAccession': 'ERA3819349',
                        'submissionError': None,
                        'sampleSameAs': None,
                        'sampleDerivedFrom': 'SAMEA12345678',
                        'sampleSymbiontOf': None}
                    ]}
        self.assertEqual(expected, response.json)

    @responses.activate
    def test_submit_and_generate_manifest_json(self):
        specimen = SubmissionsSpecimen()
        specimen.specimen_id = 'SAN1234567'
        specimen.biosample_accession = 'SAMEA12345678'
        db.session.add(specimen)
        db.session.commit()

        mock_response_from_ena = {'taxId': '6344',
                                  'scientificName': 'Arenicola marina',
                                  'commonName': 'lugworm',
                                  'formalName': 'true',
                                  'rank': 'species',
                                  'division': 'INV',
                                  'lineage': '',
                                  'geneticCode': '1',
                                  'mitochondrialGeneticCode': '5',
                                  'submittable': 'true'}
        responses.add(responses.GET, 'https://www.ebi.ac.uk/ena/taxonomy/rest/tax-id/6344',
                      json=mock_response_from_ena, status=200)
        mock_response_from_tolid = [{
            'species': {
                'commonName': 'lugworm',
                'family': 'Arenicolidae',
                'genus': 'Arenicola',
                'kingdom': 'Metazoa',
                'order': 'Capitellida',
                'phylum': 'Annelida',
                'prefix': 'wuAreMari',
                'scientificName': 'Arenicola marina',
                'taxaClass': 'Polychaeta',
                'taxonomyId': 6344
            },
            'specimen': {
                'specimenId': 'SAN1234567'
            },
            'tolId': 'wuAreMari1'
        }]
        responses.add(responses.POST, os.getenv('TOLID_URL', '') + '/tol-ids',
                      json=mock_response_from_tolid, status=200)

        mock_response_from_ena = '<?xml version="1.0" encoding="UTF-8"?><?xml-stylesheet type="text/xsl" href="receipt.xsl"?><RECEIPT receiptDate="2021-04-07T12:47:39.998+01:00" submissionFile="tmphz9luulrsubmission_3.xml" success="true"><SAMPLE accession="ERS6206028" alias="' + str(1) + '" status="PRIVATE"><EXT_ID accession="SAMEA8521239" type="biosample"/></SAMPLE><SUBMISSION accession="ERA3819349" alias="SUBMISSION-07-04-2021-12:47:36:825"/><ACTIONS>ADD</ACTIONS></RECEIPT>'  # noqa
        responses.add(responses.POST, os.getenv('ENA_URL', '') + '/ena/submit/drop-box/submit/',
                      body=mock_response_from_ena, status=200)

        body = {'samples': [
            {'row': 1,
                'SPECIMEN_ID': 'SAN1234567',
                'TAXON_ID': 6344,
                'SCIENTIFIC_NAME': 'Arenicola marina',
                'GENUS': 'Arenicola',
                'FAMILY': 'Arenicolidae',
                'ORDER_OR_GROUP': 'Scolecida',
                'COMMON_NAME': 'lugworm',
                'LIFESTAGE': 'ADULT',
                'SEX': 'FEMALE',
                'ORGANISM_PART': 'MUSCLE',
                'GAL': 'SANGER INSTITUTE',
                'GAL_SAMPLE_ID': 'SAN0000100',
                'COLLECTED_BY': 'ALEX COLLECTOR',
                'COLLECTOR_AFFILIATION': 'THE COLLECTOR INSTITUTE',
                'DATE_OF_COLLECTION': '2020-09-01',
                'COLLECTION_LOCATION': 'UNITED KINGDOM | DARK FOREST',
                'DECIMAL_LATITUDE': '+50.12345678',
                'DECIMAL_LONGITUDE': '-1.98765432',
                'HABITAT': 'Woodland',
                'IDENTIFIED_BY': 'JO IDENTIFIER',
                'IDENTIFIER_AFFILIATION': 'THE IDENTIFIER INSTITUTE',
                'VOUCHER_ID': 'voucher1'}
        ]}

        # No authorisation token given
        response = self.client.open(
            '/api/v1/manifests/generate',
            method='POST',
            json=body)
        self.assert401(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Invalid authorisation token given
        response = self.client.open(
            '/api/v1/manifests/generate',
            method='POST',
            headers={'api-key': '12345678'},
            json=body)
        self.assert401(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Not a submitter
        response = self.client.open(
            '/api/v1/manifests/generate',
            method='POST',
            headers={'api-key': self.user1.api_key},
            json=body)
        self.assert403(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Corect - should validate and return errors
        response = self.client.open(
            '/api/v1/manifests/generate',
            method='POST',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        expected = {'manifestId': 1,
                    'submissionStatus': True,
                    'projectName': 'ToL',
                    'stsManifestId': None,
                    'samples': [{
                        'row': 1,
                        'SPECIMEN_ID': 'SAN1234567',
                        'TAXON_ID': 6344,
                        'SCIENTIFIC_NAME': 'Arenicola marina',
                        'GENUS': 'Arenicola',
                        'FAMILY': 'Arenicolidae',
                        'ORDER_OR_GROUP': 'Scolecida',
                        'COMMON_NAME': 'lugworm',
                        'LIFESTAGE': 'ADULT',
                        'SEX': 'FEMALE',
                        'ORGANISM_PART': 'MUSCLE',
                        'GAL': 'SANGER INSTITUTE',
                        'GAL_SAMPLE_ID': 'SAN0000100',
                        'COLLECTED_BY': 'ALEX COLLECTOR',
                        'COLLECTOR_AFFILIATION': 'THE COLLECTOR INSTITUTE',
                        'DATE_OF_COLLECTION': '2020-09-01',
                        'COLLECTION_LOCATION': 'UNITED KINGDOM | DARK FOREST',
                        'DECIMAL_LATITUDE': '+50.12345678',
                        'DECIMAL_LONGITUDE': '-1.98765432',
                        'HABITAT': 'Woodland',
                        'IDENTIFIED_BY': 'JO IDENTIFIER',
                        'IDENTIFIER_AFFILIATION': 'THE IDENTIFIER INSTITUTE',
                        'VOUCHER_ID': 'voucher1',
                        'OTHER_INFORMATION': None,
                        'DEPTH': None,
                        'ELEVATION': None,
                        'RELATIONSHIP': None,
                        'SYMBIONT': None,
                        'CULTURE_OR_STRAIN_ID': None,
                        'SERIES': None,
                        'RACK_OR_PLATE_ID': None,
                        'TUBE_OR_WELL_ID': None,
                        'TAXON_REMARKS': None,
                        'INFRASPECIFIC_EPITHET': None,
                        'COLLECTOR_SAMPLE_ID': None,
                        'GRID_REFERENCE': None,
                        'TIME_OF_COLLECTION': None,
                        'DESCRIPTION_OF_COLLECTION_METHOD': None,
                        'DIFFICULT_OR_HIGH_PRIORITY_SAMPLE': None,
                        'IDENTIFIED_HOW': None,
                        'SPECIMEN_ID_RISK': None,
                        'PRESERVED_BY': None,
                        'PRESERVER_AFFILIATION': None,
                        'PRESERVATION_APPROACH': None,
                        'PRESERVATIVE_SOLUTION': None,
                        'TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION': None,
                        'DATE_OF_PRESERVATION': None,
                        'SIZE_OF_TISSUE_IN_TUBE': None,
                        'TISSUE_REMOVED_FOR_BARCODING': None,
                        'PLATE_ID_FOR_BARCODING': None,
                        'TUBE_OR_WELL_ID_FOR_BARCODING': None,
                        'TISSUE_FOR_BARCODING': None,
                        'BARCODE_PLATE_PRESERVATIVE': None,
                        'PURPOSE_OF_SPECIMEN': None,
                        'HAZARD_GROUP': None,
                        'REGULATORY_COMPLIANCE': None,
                        'ORIGINAL_COLLECTION_DATE': None,
                        'ORIGINAL_GEOGRAPHIC_LOCATION': None,
                        'BARCODE_HUB': None,
                        'tolId': 'wuAreMari1',
                        'biosampleAccession': 'SAMEA8521239',
                        'sraAccession': 'ERS6206028',
                        'submissionAccession': 'ERA3819349',
                        'submissionError': None,
                        'sampleSameAs': None,
                        'sampleDerivedFrom': 'SAMEA12345678',
                        'sampleSymbiontOf': None}
                    ]}
        self.assertEqual(expected, response.json)

    @responses.activate
    def test_submit_and_generate_manifest_json_unknown_taxon(self):
        specimen = SubmissionsSpecimen()
        specimen.specimen_id = 'SAN1234567'
        specimen.biosample_accession = 'SAMEA12345678'
        db.session.add(specimen)
        specimen = SubmissionsSpecimen()
        specimen.specimen_id = 'SAN7654321'
        specimen.biosample_accession = 'SAMEA87654321'
        db.session.add(specimen)
        db.session.commit()

        mock_response_from_ena = {'taxId': '6344',
                                  'scientificName': 'Arenicola marina',
                                  'commonName': 'lugworm',
                                  'formalName': 'true',
                                  'rank': 'species',
                                  'division': 'INV',
                                  'lineage': '',
                                  'geneticCode': '1',
                                  'mitochondrialGeneticCode': '5',
                                  'submittable': 'true'}
        responses.add(responses.GET, 'https://www.ebi.ac.uk/ena/taxonomy/rest/tax-id/6344',
                      json=mock_response_from_ena, status=200)
        mock_response_from_ena = {'taxId': '32644',
                                  'scientificName': 'unidentified',
                                  'formalName': 'false',
                                  'rank': 'species',
                                  'division': 'UNK',
                                  'lineage': 'unclassified sequences; ',
                                  'geneticCode': '1',
                                  'mitochondrialGeneticCode': '2',
                                  'submittable': 'true',
                                  'binomial': 'true'}
        responses.add(responses.GET, 'https://www.ebi.ac.uk/ena/taxonomy/rest/tax-id/32644',
                      json=mock_response_from_ena, status=200)
        mock_response_from_tolid = [{
            'species': {
                'commonName': 'lugworm',
                'family': 'Arenicolidae',
                'genus': 'Arenicola',
                'kingdom': 'Metazoa',
                'order': 'Capitellida',
                'phylum': 'Annelida',
                'prefix': 'wuAreMari',
                'scientificName': 'Arenicola marina',
                'taxaClass': 'Polychaeta',
                'taxonomyId': 6344
            },
            'specimen': {
                'specimenId': 'SAN1234567'
            },
            'tolId': 'wuAreMari1'
        }]
        responses.add(responses.POST, os.getenv('TOLID_URL', '') + '/tol-ids',
                      json=mock_response_from_tolid, status=200)

        mock_response_from_ena = '<?xml version="1.0" encoding="UTF-8"?><?xml-stylesheet type="text/xsl" href="receipt.xsl"?><RECEIPT receiptDate="2021-04-07T12:47:39.998+01:00" submissionFile="tmphz9luulrsubmission_3.xml" success="true"><SAMPLE accession="ERS6206028" alias="' + str(1) + '" status="PRIVATE"><EXT_ID accession="SAMEA8521239" type="biosample"/></SAMPLE><SAMPLE accession="ERS6206028" alias="' + str(2) + '" status="PRIVATE"><EXT_ID accession="SAMEA8521240" type="biosample"/></SAMPLE><SUBMISSION accession="ERA3819349" alias="SUBMISSION-07-04-2021-12:47:36:825"/><ACTIONS>ADD</ACTIONS></RECEIPT>'  # noqa
        responses.add(responses.POST, os.getenv('ENA_URL', '') + '/ena/submit/drop-box/submit/',
                      body=mock_response_from_ena, status=200)

        mock_response_from_sts = {'data': {'list': []}}
        responses.add(responses.GET, os.getenv('STS_URL', '')
                      + '/specimens?specimen_id=SAN7654321',
                      json=mock_response_from_sts, status=200)

        body = {'samples': [
            {'row': 1,
                'SPECIMEN_ID': 'SAN1234567',
                'TAXON_ID': 6344,
                'SCIENTIFIC_NAME': 'Arenicola marina',
                'GENUS': 'Arenicola',
                'FAMILY': 'Arenicolidae',
                'ORDER_OR_GROUP': 'Scolecida',
                'COMMON_NAME': 'lugworm',
                'LIFESTAGE': 'ADULT',
                'SEX': 'FEMALE',
                'ORGANISM_PART': 'MUSCLE',
                'GAL': 'SANGER INSTITUTE',
                'GAL_SAMPLE_ID': 'SAN0000100',
                'COLLECTED_BY': 'ALEX COLLECTOR',
                'COLLECTOR_AFFILIATION': 'THE COLLECTOR INSTITUTE',
                'DATE_OF_COLLECTION': '2020-09-01',
                'COLLECTION_LOCATION': 'UNITED KINGDOM | DARK FOREST',
                'DECIMAL_LATITUDE': '+50.12345678',
                'DECIMAL_LONGITUDE': '-1.98765432',
                'HABITAT': 'Woodland',
                'IDENTIFIED_BY': 'JO IDENTIFIER',
                'IDENTIFIER_AFFILIATION': 'THE IDENTIFIER INSTITUTE',
                'VOUCHER_ID': 'voucher1',
                'public_name': 'TEST1-ignored'},
            {'row': 2,
                'SPECIMEN_ID': 'SAN7654321',
                'TAXON_ID': 32644,
                'SCIENTIFIC_NAME': 'unidentified',
                'GENUS': '',
                'FAMILY': '',
                'ORDER_OR_GROUP': '',
                'COMMON_NAME': '',
                'LIFESTAGE': 'ADULT',
                'SEX': 'FEMALE',
                'ORGANISM_PART': 'MUSCLE',
                'GAL': 'SANGER INSTITUTE',
                'GAL_SAMPLE_ID': 'SAN0000100',
                'COLLECTED_BY': 'ALEX COLLECTOR',
                'COLLECTOR_AFFILIATION': 'THE COLLECTOR INSTITUTE',
                'DATE_OF_COLLECTION': '2020-09-01',
                'COLLECTION_LOCATION': 'UNITED KINGDOM | DARK FOREST',
                'DECIMAL_LATITUDE': '+50.12345678',
                'DECIMAL_LONGITUDE': '-1.98765432',
                'HABITAT': 'Woodland',
                'IDENTIFIED_BY': 'JO IDENTIFIER',
                'IDENTIFIER_AFFILIATION': 'THE IDENTIFIER INSTITUTE',
                'VOUCHER_ID': 'voucher1',
                'public_name': 'TEST2'}
        ]}

        # Correct - should validate and return errors
        response = self.client.open(
            '/api/v1/manifests/generate',
            method='POST',
            headers={'api-key': self.user3.api_key},
            json=body)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        expected = {'manifestId': 1,
                    'submissionStatus': True,
                    'projectName': 'ToL',
                    'stsManifestId': None,
                    'samples': [{
                        'row': 1,
                        'SPECIMEN_ID': 'SAN1234567',
                        'TAXON_ID': 6344,
                        'SCIENTIFIC_NAME': 'Arenicola marina',
                        'GENUS': 'Arenicola',
                        'FAMILY': 'Arenicolidae',
                        'ORDER_OR_GROUP': 'Scolecida',
                        'COMMON_NAME': 'lugworm',
                        'LIFESTAGE': 'ADULT',
                        'SEX': 'FEMALE',
                        'ORGANISM_PART': 'MUSCLE',
                        'GAL': 'SANGER INSTITUTE',
                        'GAL_SAMPLE_ID': 'SAN0000100',
                        'COLLECTED_BY': 'ALEX COLLECTOR',
                        'COLLECTOR_AFFILIATION': 'THE COLLECTOR INSTITUTE',
                        'DATE_OF_COLLECTION': '2020-09-01',
                        'COLLECTION_LOCATION': 'UNITED KINGDOM | DARK FOREST',
                        'DECIMAL_LATITUDE': '+50.12345678',
                        'DECIMAL_LONGITUDE': '-1.98765432',
                        'HABITAT': 'Woodland',
                        'IDENTIFIED_BY': 'JO IDENTIFIER',
                        'IDENTIFIER_AFFILIATION': 'THE IDENTIFIER INSTITUTE',
                        'VOUCHER_ID': 'voucher1',
                        'OTHER_INFORMATION': None,
                        'DEPTH': None,
                        'ELEVATION': None,
                        'RELATIONSHIP': None,
                        'SYMBIONT': None,
                        'CULTURE_OR_STRAIN_ID': None,
                        'SERIES': None,
                        'RACK_OR_PLATE_ID': None,
                        'TUBE_OR_WELL_ID': None,
                        'TAXON_REMARKS': None,
                        'INFRASPECIFIC_EPITHET': None,
                        'COLLECTOR_SAMPLE_ID': None,
                        'GRID_REFERENCE': None,
                        'TIME_OF_COLLECTION': None,
                        'DESCRIPTION_OF_COLLECTION_METHOD': None,
                        'DIFFICULT_OR_HIGH_PRIORITY_SAMPLE': None,
                        'IDENTIFIED_HOW': None,
                        'SPECIMEN_ID_RISK': None,
                        'PRESERVED_BY': None,
                        'PRESERVER_AFFILIATION': None,
                        'PRESERVATION_APPROACH': None,
                        'PRESERVATIVE_SOLUTION': None,
                        'TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION': None,
                        'DATE_OF_PRESERVATION': None,
                        'SIZE_OF_TISSUE_IN_TUBE': None,
                        'TISSUE_REMOVED_FOR_BARCODING': None,
                        'PLATE_ID_FOR_BARCODING': None,
                        'TUBE_OR_WELL_ID_FOR_BARCODING': None,
                        'TISSUE_FOR_BARCODING': None,
                        'BARCODE_PLATE_PRESERVATIVE': None,
                        'PURPOSE_OF_SPECIMEN': None,
                        'HAZARD_GROUP': None,
                        'REGULATORY_COMPLIANCE': None,
                        'ORIGINAL_COLLECTION_DATE': None,
                        'ORIGINAL_GEOGRAPHIC_LOCATION': None,
                        'BARCODE_HUB': None,
                        'tolId': 'wuAreMari1',
                        'biosampleAccession': 'SAMEA8521239',
                        'sraAccession': 'ERS6206028',
                        'submissionAccession': 'ERA3819349',
                        'submissionError': None,
                        'sampleSameAs': None,
                        'sampleDerivedFrom': 'SAMEA12345678',
                        'sampleSymbiontOf': None
                    }, {
                        'row': 2,
                        'SPECIMEN_ID': 'SAN7654321',
                        'TAXON_ID': 32644,
                        'SCIENTIFIC_NAME': 'unidentified',
                        'GENUS': '',
                        'FAMILY': '',
                        'ORDER_OR_GROUP': '',
                        'COMMON_NAME': None,
                        'LIFESTAGE': 'ADULT',
                        'SEX': 'FEMALE',
                        'ORGANISM_PART': 'MUSCLE',
                        'GAL': 'SANGER INSTITUTE',
                        'GAL_SAMPLE_ID': 'SAN0000100',
                        'COLLECTED_BY': 'ALEX COLLECTOR',
                        'COLLECTOR_AFFILIATION': 'THE COLLECTOR INSTITUTE',
                        'DATE_OF_COLLECTION': '2020-09-01',
                        'COLLECTION_LOCATION': 'UNITED KINGDOM | DARK FOREST',
                        'DECIMAL_LATITUDE': '+50.12345678',
                        'DECIMAL_LONGITUDE': '-1.98765432',
                        'HABITAT': 'Woodland',
                        'IDENTIFIED_BY': 'JO IDENTIFIER',
                        'IDENTIFIER_AFFILIATION': 'THE IDENTIFIER INSTITUTE',
                        'VOUCHER_ID': 'voucher1',
                        'OTHER_INFORMATION': None,
                        'DEPTH': None,
                        'ELEVATION': None,
                        'RELATIONSHIP': None,
                        'SYMBIONT': None,
                        'CULTURE_OR_STRAIN_ID': None,
                        'SERIES': None,
                        'RACK_OR_PLATE_ID': None,
                        'TUBE_OR_WELL_ID': None,
                        'TAXON_REMARKS': None,
                        'INFRASPECIFIC_EPITHET': None,
                        'COLLECTOR_SAMPLE_ID': None,
                        'GRID_REFERENCE': None,
                        'TIME_OF_COLLECTION': None,
                        'DESCRIPTION_OF_COLLECTION_METHOD': None,
                        'DIFFICULT_OR_HIGH_PRIORITY_SAMPLE': None,
                        'IDENTIFIED_HOW': None,
                        'SPECIMEN_ID_RISK': None,
                        'PRESERVED_BY': None,
                        'PRESERVER_AFFILIATION': None,
                        'PRESERVATION_APPROACH': None,
                        'PRESERVATIVE_SOLUTION': None,
                        'TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION': None,
                        'DATE_OF_PRESERVATION': None,
                        'SIZE_OF_TISSUE_IN_TUBE': None,
                        'TISSUE_REMOVED_FOR_BARCODING': None,
                        'PLATE_ID_FOR_BARCODING': None,
                        'TUBE_OR_WELL_ID_FOR_BARCODING': None,
                        'TISSUE_FOR_BARCODING': None,
                        'BARCODE_PLATE_PRESERVATIVE': None,
                        'PURPOSE_OF_SPECIMEN': None,
                        'HAZARD_GROUP': None,
                        'REGULATORY_COMPLIANCE': None,
                        'ORIGINAL_COLLECTION_DATE': None,
                        'ORIGINAL_GEOGRAPHIC_LOCATION': None,
                        'BARCODE_HUB': None,
                        'tolId': 'TEST2',
                        'biosampleAccession': 'SAMEA8521240',
                        'sraAccession': 'ERS6206028',
                        'submissionAccession': 'ERA3819349',
                        'submissionError': None,
                        'sampleSameAs': None,
                        'sampleDerivedFrom': 'SAMEA87654321',
                        'sampleSymbiontOf': None}
                    ]}
        self.assertEqual(expected, response.json)


if __name__ == '__main__':
    import unittest
    unittest.main()
