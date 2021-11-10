# SPDX-FileCopyrightText: 2021 Genome Research Ltd.
#
# SPDX-License-Identifier: MIT

from __future__ import absolute_import

from test import BaseTestCase
from main.model import SubmissionsSample, SubmissionsManifest


class TestSubmissionsSample(BaseTestCase):

    def test_unique_taxonomy_ids(self):
        manifest = SubmissionsManifest()
        sample = SubmissionsSample()
        sample.taxonomy_id = 1
        sample.manifest = manifest
        sample = SubmissionsSample()
        sample.taxonomy_id = 1
        sample.manifest = manifest
        sample = SubmissionsSample()
        sample.taxonomy_id = 2
        sample.manifest = manifest

        expected = set([1, 2])

        self.assertEqual(expected, manifest.unique_taxonomy_ids())


if __name__ == '__main__':
    import unittest
    unittest.main()
