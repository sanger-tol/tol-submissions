# SPDX-FileCopyrightText: 2021 Genome Research Ltd.
#
# SPDX-License-Identifier: MIT

import os
from test import BaseTestCase

from flask import json

from main.model import SubmissionsSample, SubmissionsSpecimen, db

import responses


def create_sample(biosample_id):
    # instantiate sample
    sample = SubmissionsSample()

    # fill in fields
    sample.biosample_accession = biosample_id
    sample.row = 0
    sample.specimen_id = 'SAN1234567'
    sample.taxonomy_id = 6344
    sample.scientific_name = 'Arenicola marina'
    sample.family = 'Arenicolidae'
    sample.genus = 'Arenicola'
    sample.common_name = 'lugworm'
    sample.order_or_group = 'Scolecida'
    sample.lifestage = 'ADULT'
    sample.sex = 'FEMALE'
    sample.organism_part = 'MUSCLE'
    sample.GAL = 'SANGER INSTITUTE'
    sample.GAL_sample_id = 'SAN0000100'
    sample.collected_by = 'ALEX COLLECTOR'
    sample.collector_affiliation = 'THE COLLECTOR INSTITUTE'
    sample.date_of_collection = '2020-09-01'
    sample.collection_location = 'UNITED KINGDOM | DARK FOREST'
    sample.decimal_latitude = '+50.12345678'
    sample.decimal_longitude = '-1.98765432'
    sample.habitat = 'Woodland'
    sample.identified_by = 'JO IDENTIFIER'
    sample.identifier_affiliation = 'THE IDENTIFIER INSTITUTE'
    sample.voucher_id = ''

    return sample


def create_three_samples_for_specimen(biospecimen_id, biosample_ids):
    # instantiate the three samples, with specified biosample ID's
    same_sample = create_sample(biosample_ids[0])
    derived_sample = create_sample(biosample_ids[1])
    symbiont_sample = create_sample(biosample_ids[2])

    # set their respective "biospecimen ID's"
    same_sample.sample_same_as = biospecimen_id
    derived_sample.sample_derived_from = biospecimen_id
    symbiont_sample.sample_symbiont_of = biospecimen_id

    # return the samples as a list
    return [same_sample, derived_sample, symbiont_sample]


def create_specimen(specimen_id, biospecimen_id):
    # instantiate specimen
    specimen = SubmissionsSpecimen()

    # fill in fields
    specimen.specimen_id = specimen_id
    specimen.biosample_accession = biospecimen_id

    return specimen


def assert_samples_are_same(obj, inserted_sample, retrieved_sample_dict):
    # convert both to dictionaries
    inserted_sample_dict = inserted_sample.to_dict()

    obj.assertEqual(inserted_sample_dict, retrieved_sample_dict)


def assert_inserted_and_retrieved_are_same(obj, inserted, retrieved):
    """
    Compares the inserted samples, and retrived samples, by
    creating a list of json representations (dicts are not
    hashable), and then comparing a set of each to account
    for different orderings
    """
    # get the set of inserted samples as json
    inserted_set = {json.dumps(p.to_dict()) for p in inserted}

    # assert that the length is the same, to detect duplicates
    # in the inserted samples
    obj.assertEqual(
        len(inserted),
        len(inserted_set),
    )

    # get the set of retrieved samples as json
    retrieved_set = {json.dumps(r) for r in retrieved}

    # assert that the length is the same, to detect duplicates
    # in the retrieved samples
    obj.assertEqual(
        len(retrieved),
        len(retrieved_set)
    )

    obj.assertEqual(
        inserted_set,
        retrieved_set,
    )


class TestUsersController(BaseTestCase):
    def test_get_sample(self):
        # obviously invalid sample ID
        invalid_biosample_id = 'doesntMatterAtAll'
        response = self.client.open(
            f'/api/v1/samples/{invalid_biosample_id}',
            method='GET',
        )
        self.assert404(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # previously inserted sample ID
        inserted_biosample_id = 'aBrilliantBiosampleId'
        inserted_sample = create_sample(inserted_biosample_id)
        db.session.add(inserted_sample)
        db.session.commit()
        response = self.client.open(
            f'/api/v1/samples/{inserted_biosample_id}',
            method='GET',
        )
        # assert that the sample was found
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        # assert that inserted and retrieved are the same
        assert_samples_are_same(self, inserted_sample, response.json)

    @responses.activate
    def test_get_samples_by_specimen_id(self):
        # obviously invalid specimen ID
        invalid_specimen_id = 'doesntMatterAtAll'
        # mock STS Call
        responses.add(responses.GET, os.environ['STS_URL'] + '/specimens?specimen_id='
                      + invalid_specimen_id,
                      json={'data': {'list': []}},
                      status=200)
        response = self.client.open(
            f'/api/v1/specimens/specimenId/{invalid_specimen_id}/samples',
            method='GET',
        )
        self.assert404(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        # reset the mock
        responses.reset()

        # insert specimen with one of each kind of sample
        present_specimen_id = 'specimenIdNova'
        present_biospecimen_id = 'biospecimenIdNova'
        present_biosample_ids = [
            'thing1',
            'thing2',
            'thing3',
        ]
        # mock STS Call
        responses.add(responses.GET, os.environ['STS_URL'] + '/specimens?specimen_id='
                      + present_specimen_id,
                      json={'data': {'list': [
                          {'specimen_id': present_specimen_id,
                           'bio_specimen_id': present_biospecimen_id}
                      ]}},
                      status=200)
        present_samples = create_three_samples_for_specimen(
            present_biospecimen_id,
            present_biosample_ids,
        )
        db.session.add_all(present_samples)
        db.session.commit()

        # request for this specimen's samples at the specimen ID endpoint
        response = self.client.open(
            f'/api/v1/specimens/specimenId/{present_specimen_id}/samples',
            method='GET',
        )

        # assert that the specimen was found
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # assert that the biospecimen ID is correct
        self.assertEqual(present_biospecimen_id, response.json['biospecimenId'])

        # assert that all 3 samples were found for this present specimen
        retrieved_samples = response.json['samples']
        assert_inserted_and_retrieved_are_same(
            self,
            present_samples,
            retrieved_samples,
        )

        # reset the responses
        responses.reset()

    @responses.activate
    def test_get_samples_by_biospecimen_id(self):
        # obviously invalid biospecimen ID
        invalid_biospecimen_id = 'andNothingElseMatters'
        # mock STS Call
        responses.add(responses.GET, os.environ['STS_URL'] + '/specimens?bio_specimen_id='
                      + invalid_biospecimen_id,
                      json={'data': {'list': []}},
                      status=200)
        response = self.client.open(
            f'/api/v1/specimens/biospecimenId/{invalid_biospecimen_id}/samples',
            method='GET',
        )
        self.assert404(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        # reset the mock
        responses.reset()

        # insert specimen with one of each kind of sample
        present_specimen_id = 'uberSpecimenId'
        present_biospecimen_id = 'uberBioSpecimenId'
        present_biosample_ids = [
            'another1',
            'another2',
            'another3',
        ]
        # mock STS Call
        responses.add(responses.GET, os.environ['STS_URL'] + '/specimens?bio_specimen_id='
                      + present_biospecimen_id,
                      json={'data': {'list': [
                          {'specimen_id': present_specimen_id,
                           'bio_specimen_id': present_biospecimen_id}
                      ]}},
                      status=200)
        present_samples = create_three_samples_for_specimen(
            present_biospecimen_id,
            present_biosample_ids,
        )
        db.session.add_all(present_samples)
        db.session.commit()

        # request for this specimen's samples at the biospecimen ID endpoint
        response = self.client.open(
            f'/api/v1/specimens/biospecimenId/{present_biospecimen_id}/samples',
            method='GET',
        )

        # assert that the specimen was found
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

        # assert that the specimen ID is correct
        self.assertEqual(present_specimen_id, response.json['specimenId'])

        # assert that all 3 samples were found for this present specimen
        retrieved_samples = response.json['samples']
        assert_inserted_and_retrieved_are_same(
            self,
            present_samples,
            retrieved_samples,
        )


if __name__ == '__main__':
    import unittest
    unittest.main()
