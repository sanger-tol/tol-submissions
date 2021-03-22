from __future__ import absolute_import

from swagger_server.test import BaseTestCase
# from openpyxl import load_workbook


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
            headers={"api-key": "12345678"},
            json=body)
        self.assert401(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Body empty
        body = {}
        response = self.client.open(
            '/api/v1/manifests',
            method='POST',
            headers={"api-key": self.user3.api_key},
            json=body)
        self.assert400(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Not a submitter
        body = {'manifestId': 'manifest1234',
                'samples': [
                    {'sampleId': 'sample5678',
                     'specimenId': 'specimen9876',
                     'taxonomyId': 6344}
                ]}
        response = self.client.open(
            '/api/v1/manifests',
            method='POST',
            headers={"api-key": self.user1.api_key},
            json=body)
        self.assert403(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Correct, minimal JSON
        body = {'manifestId': 'manifest1234',
                'samples': [
                    {'sampleId': 'sample5678',
                     'specimenId': 'specimen9876',
                     'taxonomyId': 6344}
                ]}
        response = self.client.open(
            '/api/v1/manifests',
            method='POST',
            headers={"api-key": self.user3.api_key},
            json=body)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        expected = {'manifestId': 'manifest1234',
                    'samples': [
                        {'sampleId': 'sample5678',
                         'specimenId': 'specimen9876',
                         'taxonomyId': 6344,
                         'scientificName': None,
                         'commonName': None,
                         'biosampleId': None,
                         'lifestage': None,
                         'sex': None,
                         'organismPart': None,
                         'GAL': None,
                         'GALSampleId': None,
                         'collectedBy': None,
                         'collectorAffiliation': None,
                         'dateOfCollection': None,
                         'collectionLocation': None,
                         'decimalLatitude': None,
                         'decimalLongitude': None,
                         'habitat': None,
                         'identifiedBy': None,
                         'identifierAffiliation': None,
                         'voucherId': None,
                         'tolId': None}
                    ]}
        self.assertEquals(expected, response.json)

        # Submit again - should get error
        body = {'manifestId': 'manifest1234',
                'samples': [
                    {'sampleId': 'sample5678',
                     'specimenId': 'specimen9876',
                     'taxonomyId': 6344}
                ]}
        response = self.client.open(
            '/api/v1/manifests',
            method='POST',
            headers={"api-key": self.user3.api_key},
            json=body)
        self.assert400(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Correct, full JSON
        body = {'manifestId': 'manifest2345',
                'samples': [
                    {'sampleId': 'sample6789',
                     'specimenId': 'specimen9876',
                     'taxonomyId': 6344,
                     'scientificName': 'Arenicola marina',
                     'commonName': 'lugworm',
                     'biosampleId': 'SAMEA12345678',
                     'lifestage': 'ADULT',
                     'sex': 'FEMALE',
                     'organismPart': 'MUSCLE',
                     'GAL': 'SANGER INSTITUTE',
                     'GALSampleId': 'SAN000100',
                     'collectedBy': 'ALEX COLLECTOR',
                     'collectorAffiliation': 'THE COLLECTOR INSTITUTE',
                     'dateOfCollection': '2020-09-01',
                     'collectionLocation': 'UK | DARK FOREST',
                     'decimalLatitude': '+50.12345678',
                     'decimalLongitude': '-1.98765432',
                     'habitat': 'Woodland',
                     'identifiedBy': 'JO IDENTIFIER',
                     'identifierAffiliation': 'THE IDENTIFIER INSTITUTE',
                     'voucherId': 'voucher1',
                     'tolId': 'wuAreMari1'}
                ]}
        response = self.client.open(
            '/api/v1/manifests',
            method='POST',
            headers={"api-key": self.user3.api_key},
            json=body)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        expected = {'manifestId': 'manifest2345',
                    'samples': [
                        {'sampleId': 'sample6789',
                         'specimenId': 'specimen9876',
                         'taxonomyId': 6344,
                         'scientificName': 'Arenicola marina',
                         'commonName': 'lugworm',
                         'biosampleId': None,
                         'lifestage': 'ADULT',
                         'sex': 'FEMALE',
                         'organismPart': 'MUSCLE',
                         'GAL': 'SANGER INSTITUTE',
                         'GALSampleId': 'SAN000100',
                         'collectedBy': 'ALEX COLLECTOR',
                         'collectorAffiliation': 'THE COLLECTOR INSTITUTE',
                         'dateOfCollection': '2020-09-01',
                         'collectionLocation': 'UK | DARK FOREST',
                         'decimalLatitude': '+50.12345678',
                         'decimalLongitude': '-1.98765432',
                         'habitat': 'Woodland',
                         'identifiedBy': 'JO IDENTIFIER',
                         'identifierAffiliation': 'THE IDENTIFIER INSTITUTE',
                         'voucherId': 'voucher1',
                         'tolId': None}
                    ]}
        self.assertEquals(expected, response.json)


if __name__ == '__main__':
    import unittest
    unittest.main()
