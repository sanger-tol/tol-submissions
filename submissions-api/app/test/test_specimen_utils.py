from __future__ import absolute_import

from test import BaseTestCase

from main.specimen_utils import get_specimen_sts, get_biospecimen_sts

import responses
import os


class TestSpecimenUtils(BaseTestCase):

    @responses.activate
    def test_get_specimen_sts(self):
        specimen_id = "a_great_specimen_id"
        url = os.environ['STS_URL'] + '/specimens?specimen_id=' + specimen_id

        # no elements in list
        mock_no_elements = {
            "data": {
                "list": []
            }
        }

        responses.add(responses.GET, url, json=mock_no_elements, status=200)
        result = get_specimen_sts(specimen_id)
        expected = None
        self.assertEqual(result, expected)

        # reset the mock
        responses.reset()

        # too many elements in list
        mock_too_many = {
            "data": {
                "list": [
                    {
                        "bio_specimen_id": "test_bio_specimen_id",
                        "specimen_id": "test_specimen_id"
                    },
                    {
                        "bio_specimen_id": "superfluous_bio_specimen_id",
                        "specimen_id": "superfluous_specimen_id"
                    }
                ]
            }
        }

        responses.add(responses.GET, url, json=mock_too_many, status=200)
        result = get_specimen_sts(specimen_id)
        expected = None
        self.assertEqual(result, expected)

        # reset the mock
        responses.reset()

        # successfully returning a single specimen
        mock_specimen_sts = {
            "data": {
                "list": [
                    {
                        "bio_specimen_id": "test_bio_specimen_id",
                        "specimen_id": "test_specimen_id"
                    }
                ]
            }
        }

        responses.add(responses.GET, url, json=mock_specimen_sts, status=200)
        result = get_specimen_sts(specimen_id)
        self.assertEqual(result.biosample_accession, "test_bio_specimen_id")
        self.assertEqual(result.specimen_id, "test_specimen_id")

        # reset the mock
        responses.reset()

    @responses.activate
    def test_get_biospecimen_sts(self):
        biospecimen_id = "a_great_biospecimen_id"
        url = os.environ['STS_URL'] + '/specimens?bio_specimen_id=' + biospecimen_id

        # no elements in list
        mock_no_elements = {
            "data": {
                "list": []
            }
        }

        responses.add(responses.GET, url, json=mock_no_elements, status=200)
        result = get_biospecimen_sts(biospecimen_id)
        expected = None
        self.assertEqual(result, expected)

        # reset the mock
        responses.reset()

        # too many elements in list
        mock_too_many = {
            "data": {
                "list": [
                    {
                        "bio_specimen_id": "test_bio_specimen_id",
                        "specimen_id": "test_specimen_id"
                    },
                    {
                        "bio_specimen_id": "superfluous_bio_specimen_id",
                        "specimen_id": "superfluous_specimen_id"
                    }
                ]
            }
        }

        responses.add(responses.GET, url, json=mock_too_many, status=200)
        result = get_biospecimen_sts(biospecimen_id)
        expected = None
        self.assertEqual(result, expected)

        # reset the mock
        responses.reset()

        # successfully returning a single specimen
        mock_specimen_sts = {
            "data": {
                "list": [
                    {
                        "bio_specimen_id": "test_bio_specimen_id",
                        "specimen_id": "test_specimen_id"
                    }
                ]
            }
        }

        responses.add(responses.GET, url, json=mock_specimen_sts, status=200)
        result = get_biospecimen_sts(biospecimen_id)
        self.assertEqual(result.biosample_accession, "test_bio_specimen_id")
        self.assertEqual(result.specimen_id, "test_specimen_id")

        # reset the mock
        responses.reset()


if __name__ == '__main__':
    import unittest
    unittest.main()
