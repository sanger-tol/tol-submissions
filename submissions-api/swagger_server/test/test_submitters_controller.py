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

        body = {'samples': [
                    {'row': 1,
                     'SPECIMEN_ID': 'specimen9876',
                     'TAXON_ID': 6344,
                     'SCIENTIFIC_NAME': 'Arenicola marina',
                     'COMMON_NAME': 'lugworm',
                     'LIFESTAGE': 'ADULT',
                     'SEX': 'FEMALE',
                     'ORGANISM_PART': 'MUSCLE',
                     'GAL': 'SANGER INSTITUTE',
                     'GAL_SAMPLE_ID': 'SAN000100',
                     'COLLECTED_BY': 'ALEX COLLECTOR',
                     'COLLECTOR_AFFILIATION': 'THE COLLECTOR INSTITUTE',
                     'DATE_OF_COLLECTION': '2020-09-01',
                     'COLLECTION_LOCATION': 'UK | DARK FOREST',
                     'DECIMAL_LATITUDE': '+50.12345678',
                     'DECIMAL_LONGITUDE': '-1.98765432',
                     'HABITAT': 'Woodland',
                     'IDENTIFIED_BY': 'JO IDENTIFIER',
                     'IDENTIFIER_AFFILIATION': 'THE IDENTIFIER INSTITUTE',
                     'VOUCHER_ID': 'voucher1',
                     'tolId': 'wuAreMari1',
                     'biosampleId': 'SAMEA12345678'}
                ]}
        # Not a submitter
        response = self.client.open(
            '/api/v1/manifests',
            method='POST',
            headers={"api-key": self.user1.api_key},
            json=body)
        self.assert403(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Correct, full JSON
        response = self.client.open(
            '/api/v1/manifests',
            method='POST',
            headers={"api-key": self.user3.api_key},
            json=body)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        expected = {'manifestId': 1,
                    'samples': [
                        {'row': 1,
                         'SPECIMEN_ID': 'specimen9876',
                         'TAXON_ID': 6344,
                         'SCIENTIFIC_NAME': 'Arenicola marina',
                         'COMMON_NAME': 'lugworm',
                         'LIFESTAGE': 'ADULT',
                         'SEX': 'FEMALE',
                         'ORGANISM_PART': 'MUSCLE',
                         'GAL': 'SANGER INSTITUTE',
                         'GAL_SAMPLE_ID': 'SAN000100',
                         'COLLECTED_BY': 'ALEX COLLECTOR',
                         'COLLECTOR_AFFILIATION': 'THE COLLECTOR INSTITUTE',
                         'DATE_OF_COLLECTION': '2020-09-01',
                         'COLLECTION_LOCATION': 'UK | DARK FOREST',
                         'DECIMAL_LATITUDE': '+50.12345678',
                         'DECIMAL_LONGITUDE': '-1.98765432',
                         'HABITAT': 'Woodland',
                         'IDENTIFIED_BY': 'JO IDENTIFIER',
                         'IDENTIFIER_AFFILIATION': 'THE IDENTIFIER INSTITUTE',
                         'VOUCHER_ID': 'voucher1',
                         'HEIGHT': None,
                         'DEPTH': None,
                         'RELATIONSHIP': None,
                         'tolId': None,
                         'biosampleId': None}
                    ]}
        self.assertEquals(expected, response.json)


if __name__ == '__main__':
    import unittest
    unittest.main()
