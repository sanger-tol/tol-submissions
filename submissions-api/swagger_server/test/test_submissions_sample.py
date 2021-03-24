from __future__ import absolute_import

from swagger_server.test import BaseTestCase

from swagger_server.model import SubmissionsSample


class TestSubmissionsSample(BaseTestCase):

    def test_country_region(self):
        sample = SubmissionsSample()

        # Correct
        sample.collection_location = "United Kingdom | England | Cambridge"
        self.assertEqual(sample.collection_country(), "United Kingdom")
        self.assertEqual(sample.collection_region(), "England | Cambridge")

        # Only country
        sample.collection_location = "United Kingdom"
        self.assertEqual(sample.collection_country(), "United Kingdom")
        self.assertEqual(sample.collection_region(), "")

        # Blank
        sample.collection_location = ""
        self.assertEqual(sample.collection_country(), "")
        self.assertEqual(sample.collection_region(), "")


if __name__ == '__main__':
    import unittest
    unittest.main()
