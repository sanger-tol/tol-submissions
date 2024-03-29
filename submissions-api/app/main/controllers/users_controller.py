# SPDX-FileCopyrightText: 2021 Genome Research Ltd.
#
# SPDX-License-Identifier: MIT

import logging
import os

from flask import jsonify

from main.model import SubmissionsSample, db
from main.specimen_utils import get_biospecimen_sts, get_specimen_sts

from sqlalchemy import or_


def get_samples_from_specimen(specimen):
    # get the biospecimen ID from specimen
    biosspecimen_id = specimen.biosample_accession

    # Get all the samples from this specimen
    samples = db.session.query(SubmissionsSample) \
        .filter(or_(
            SubmissionsSample.sample_same_as == biosspecimen_id,
            SubmissionsSample.sample_derived_from == biosspecimen_id,
            SubmissionsSample.sample_symbiont_of == biosspecimen_id,
        )) \
        .all()

    return jsonify({
        'specimenId': specimen.specimen_id,
        'biospecimenId': biosspecimen_id,
        'samples': samples,
    })


def get_samples_by_specimen_id(specimen_id):
    # Does the specimen exist?
    specimen = get_specimen_sts(specimen_id)
    if specimen is None:
        return jsonify({'detail': 'Specimen does not exist'}), 404

    # return the samples
    return get_samples_from_specimen(specimen)


def get_samples_by_biospecimen_id(biospecimen_id):
    """
    Gets the samples matching the biospecimen ID
    of a specimen
    """
    # Does the specimen exist?
    specimen = get_biospecimen_sts(biospecimen_id)
    if specimen is None:
        return jsonify({'detail': 'Specimen does not exist'}), 404

    # return the samples
    return get_samples_from_specimen(specimen)


def get_sample(biosample_id):
    # Does the sample exist?
    sample = db.session.query(SubmissionsSample) \
        .filter(SubmissionsSample.biosample_accession == biosample_id) \
        .one_or_none()
    if sample is None:
        return jsonify({'detail': 'Sample does not exist'}), 404

    return jsonify(sample)


def get_environment():
    deployment_environment = os.getenv('ENVIRONMENT')
    if deployment_environment is not None and deployment_environment != '':
        return jsonify({'environment': deployment_environment})

    # if unset, return error
    logging.warn('$ENVIRONMENT is unset - this should probably be "dev"')
    return jsonify({'environment': 'dev'})
