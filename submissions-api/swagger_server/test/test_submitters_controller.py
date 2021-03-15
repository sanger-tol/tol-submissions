from __future__ import absolute_import

from swagger_server.test import BaseTestCase
# from openpyxl import load_workbook


class TestSubmittersController(BaseTestCase):

    def test_submit_manifest(self):
        # No authorisation token given
        body = []
        response = self.client.open(
            '/api/v1/submit-manifest',
            method='POST',
            json=body)
        self.assert401(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        # Invalid authorisation token given
        body = []
        response = self.client.open(
            '/api/v1/submit-manifest',
            method='POST',
            headers={"api-key": "12345678"},
            json=body)
        self.assert401(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Excel file missing
        data = {}
        response = self.client.open(
            '/api/v1/submit-manifest',
            method='POST',
            headers={"api-key": self.user1.api_key},
            data=data)
        self.assert400(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # Excel file with no taxon ID, specimen ID, ToLID column
        file = open('swagger_server/test/test-manifest-no-columns.xlsx', 'rb')
        data = {
            'excelFile': (file, 'test_file.xlsx'),
        }
        expected = {'errors': [{'message': 'Cannot find Taxon ID column'},
                               {'message': 'Cannot find Specimen ID column'},
                               {'message': 'Cannot find ToLID column'}]}
        response = self.client.open(
            '/api/v1/submit-manifest',
            method='POST',
            headers={"api-key": self.user3.api_key},
            data=data)
        file.close()
        self.assert400(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        self.assertEquals(expected, response.json)

        # Excel file with errors
        file = open('swagger_server/test/test-manifest-with-errors.xlsx', 'rb')
        data = {
            'excelFile': (file, 'test_file.xlsx'),
        }
        expected = {'errors':
                    [{'message': 'Row 2: Expecting Arenicola marina, got Homo sapiens'},
                     {'message': 'Row 3: Taxon ID 9999999 cannot be found'},
                     {'message': 'Row 4: Genus only for Arenicola sp., not assigning ToLID'}]}
        response = self.client.open(
            '/api/v1/submit-manifest',
            method='POST',
            headers={"api-key": self.user3.api_key},
            data=data)
        file.close()
        self.assert400(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        self.assertEquals(expected, response.json)

        # User not a submitter
        file = open('swagger_server/test/test-manifest.xlsx', 'rb')
        data = {
            'excelFile': (file, 'test_file.xlsx'),
        }
        response = self.client.open(
            '/api/v2/validate-manifest',
            method='POST',
            headers={"api-key": self.user1.api_key},
            data=data)
        file.close()
        self.assert403(response, 'Not received a 403 response')

        # Excel file correct
        file = open('swagger_server/test/test-manifest.xlsx', 'rb')
        data = {
            'excelFile': (file, 'test_file.xlsx'),
        }
        response = self.client.open(
            '/api/v1/submit-manifest',
            method='POST',
            headers={"api-key": self.user3.api_key},
            data=data)
        file.close()
        self.assert200(response, 'Not received a 200 response')
        self.assertEquals('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                          response.content_type)

        # Save as Excel file
        file = open('swagger_server/test/test-manifest-submitted.xlsx', 'wb')
        file.write(response.get_data())
        file.close()
        # This is where we need to assert that the columns have been filled in
        # workbook = load_workbook(filename='swagger_server/test/test-manifest-submitted.xlsx')
        # sheet = workbook.active
        # (taxon_id_column, specimen_id_column, scientific_name_column, tol_id_column) = \
        #    find_columns(sheet, "scientific_name")
        # self.assertEquals('wuAreMari3', sheet.cell(row=2, column=tol_id_column).value)
        # self.assertEquals('wuAreMari4', sheet.cell(row=3, column=tol_id_column).value)
        # self.assertEquals('wuAreMari4', sheet.cell(row=4, column=tol_id_column).value)


if __name__ == '__main__':
    import unittest
    unittest.main()
