# SPDX-FileCopyrightText: 2021 Genome Research Ltd.
#
# SPDX-License-Identifier: MIT

import os

import connexion

from flask import jsonify

import main.manifest_utils as manifest_utils
from main.model import SubmissionsManifest, SubmissionsRole, \
    SubmissionsSample, SubmissionsUser, db

import requests

from sqlalchemy import or_


def get_manifests():
    role = db.session.query(SubmissionsRole) \
        .filter(or_(SubmissionsRole.role == 'submitter', SubmissionsRole.role == 'admin')) \
        .filter(SubmissionsRole.user_id == connexion.context['user']) \
        .one_or_none()
    if role is None:
        return jsonify({'detail': 'User does not have permission to use this function'}), 403
    manifests = db.session.query(SubmissionsManifest) \
        .order_by(SubmissionsManifest.manifest_id.desc()) \
        .all()

    return jsonify([manifest.to_dict_short() for manifest in manifests])


def upload_manifest_json(body={}, excel_file=None):  # noqa: E501
    role = db.session.query(SubmissionsRole) \
        .filter(or_(SubmissionsRole.role == 'submitter', SubmissionsRole.role == 'admin')) \
        .filter(SubmissionsRole.user_id == connexion.context['user']) \
        .one_or_none()
    if role is None:
        return jsonify({'detail': 'User does not have permission to use this function'}), 403
    user = db.session.query(SubmissionsUser) \
        .filter(SubmissionsUser.user_id == connexion.context['user']) \
        .one_or_none()

    manifest = manifest_utils.create_manifest_from_json(body, user)
    db.session.add(manifest)
    db.session.commit()
    return jsonify(manifest)


def get_manifest(manifest_id=None):
    role = db.session.query(SubmissionsRole) \
        .filter(or_(SubmissionsRole.role == 'submitter', SubmissionsRole.role == 'admin')) \
        .filter(SubmissionsRole.user_id == connexion.context['user']) \
        .one_or_none()
    if role is None:
        return jsonify({'detail': 'User does not have permission to use this function'}), 403

    # Does the manifest exist?
    manifest = db.session.query(SubmissionsManifest) \
        .filter(SubmissionsManifest.manifest_id == manifest_id) \
        .one_or_none()
    if manifest is None:
        return jsonify({'detail': 'Manifest does not exist'}), 404

    return jsonify(manifest)


def fill_manifest(manifest_id=None):
    role = db.session.query(SubmissionsRole) \
        .filter(or_(SubmissionsRole.role == 'submitter', SubmissionsRole.role == 'admin')) \
        .filter(SubmissionsRole.user_id == connexion.context['user']) \
        .one_or_none()
    if role is None:
        return jsonify({'detail': 'User does not have permission to use this function'}), 403

    # Does the manifest exist?
    manifest = db.session.query(SubmissionsManifest) \
        .filter(SubmissionsManifest.manifest_id == manifest_id) \
        .one_or_none()
    if manifest is None:
        return jsonify({'detail': 'Manifest does not exist'}), 404

    ncbi_data = manifest_utils.get_ncbi_data(manifest)
    for sample in manifest.samples:
        # Call out to STS for the sample data. No this is a bit of a fudge because we have to
        # choose a sample from the specimen which only really works if we don't resample the
        # same specimen.
        response = requests.post(os.getenv('STS_URL') + '/samples',
                                 json={'specimen_specimen_id': sample.specimen_id},
                                 headers={'Project': 'ALL',
                                          'Authorization': os.getenv('STS_API_KEY')})
        if (response.status_code != 200):
            return jsonify({'detail': 'Specimen does not exist in STS: '
                           + sample.specimen_id}), 404
        samples = response.json()['data']['list']
        if len(samples) < 1:
            return jsonify({'detail': 'Samples do not exist in STS: ' + sample.specimen_id}), 404

        # We don't get all the info we need on this endpoint, so we will use this to call
        # another endpoint which does have the details
        rack_id = samples[0].get('sample_rackid', None)
        tube_id = samples[0].get('sample_tubeid', None)
        response = requests.get(os.getenv('STS_URL') + '/samples/detail',
                                params={'rack_id': rack_id,
                                        'tube_id': tube_id},
                                headers={'Project': 'ALL',
                                         'Authorization': os.getenv('STS_API_KEY')})
        if (response.status_code != 200):
            return jsonify({'detail': 'Specimen does not exist in STS: '
                           + sample.specimen_id}), 404
        sample_from_sts = response.json()['data']
        if len(sample_from_sts) < 1:
            return jsonify({'detail': 'Sample does not exist in STS: ' + sample.specimen_id}), 404

        for field in SubmissionsSample.all_fields:
            if 'sts_api_name' in field:
                val = sample_from_sts.get(field['sts_api_name'], None)
                if val == '':
                    val = None
                current_val = getattr(sample, field['python_name'])
                if current_val is None:
                    setattr(sample, field['python_name'], val)

        # NCBI for the taxonomy
        if sample.taxonomy_id not in ncbi_data:
            return jsonify({'detail': 'Taxon ID does not exist in NCBI: '
                           + str(sample.taxonomy_id)}), 404

        ncbi_result = ncbi_data[sample.taxonomy_id]

        # Go through the lineage
        for element in ncbi_result['LineageEx']:
            rank = element.get('Rank')
            if rank == 'genus':
                sample.genus = element.get('ScientificName')
            elif rank == 'family':
                sample.family = element.get('ScientificName')
            elif rank == 'order':
                sample.order_or_group = element.get('ScientificName').upper()

    db.session.commit()
    return jsonify(manifest)


def validate_manifest(manifest_id=None):
    # Do the validation here
    role = db.session.query(SubmissionsRole) \
        .filter(or_(SubmissionsRole.role == 'submitter', SubmissionsRole.role == 'admin')) \
        .filter(SubmissionsRole.user_id == connexion.context['user']) \
        .one_or_none()
    if role is None:
        return jsonify({'detail': 'User does not have permission to use this function'}), 403

    # Does the manifest exist?
    manifest = db.session.query(SubmissionsManifest) \
        .filter(SubmissionsManifest.manifest_id == manifest_id) \
        .one_or_none()
    if manifest is None:
        return jsonify({'detail': 'Manifest does not exist'}), 404

    number_of_errors, validation_results = manifest_utils.validate_manifest(manifest)
    return jsonify({'manifestId': manifest.manifest_id,
                    'number_of_errors': number_of_errors,
                    'validations': validation_results})


def submit_and_validate_manifest_json(body=None):
    role = db.session.query(SubmissionsRole) \
        .filter(or_(SubmissionsRole.role == 'submitter', SubmissionsRole.role == 'admin')) \
        .filter(SubmissionsRole.user_id == connexion.context['user']) \
        .one_or_none()
    if role is None:
        return jsonify({'detail': 'User does not have permission to use this function'}), 403

    user = db.session.query(SubmissionsUser) \
        .filter(SubmissionsUser.user_id == connexion.context['user']) \
        .one_or_none()

    # Add the manifest
    manifest = manifest_utils.create_manifest_from_json(body, user)

    db.session.add(manifest)
    db.session.commit()

    # Validate the manifest
    number_of_errors, validation_results = manifest_utils.validate_manifest(manifest)
    return jsonify({'manifestId': manifest.manifest_id,
                    'number_of_errors': number_of_errors,
                    'validations': validation_results})


def generate_ids_for_manifest(manifest_id=None):
    # Do the validation here
    role = db.session.query(SubmissionsRole) \
        .filter(or_(SubmissionsRole.role == 'submitter', SubmissionsRole.role == 'admin')) \
        .filter(SubmissionsRole.user_id == connexion.context['user']) \
        .one_or_none()
    if role is None:
        return jsonify({'detail': 'User does not have permission to use this function'}), 403

    # Does the manifest exist?
    manifest = db.session.query(SubmissionsManifest) \
        .filter(SubmissionsManifest.manifest_id == manifest_id) \
        .one_or_none()
    if manifest is None:
        return jsonify({'detail': 'Manifest does not exist'}), 404

    number_of_errors, validation_results = manifest_utils.generate_ids_for_manifest(manifest)

    if number_of_errors > 0:
        return jsonify({'manifestId': manifest.manifest_id,
                        'number_of_errors': number_of_errors,
                        'validations': validation_results})

    return jsonify(manifest)


def submit_and_generate_manifest_json(body=None):
    role = db.session.query(SubmissionsRole) \
        .filter(or_(SubmissionsRole.role == 'submitter', SubmissionsRole.role == 'admin')) \
        .filter(SubmissionsRole.user_id == connexion.context['user']) \
        .one_or_none()
    if role is None:
        return jsonify({'detail': 'User does not have permission to use this function'}), 403

    user = db.session.query(SubmissionsUser) \
        .filter(SubmissionsUser.user_id == connexion.context['user']) \
        .one_or_none()

    # Add the manifest
    manifest = manifest_utils.create_manifest_from_json(body, user)

    db.session.add(manifest)
    db.session.commit()

    number_of_errors, validation_results = manifest_utils.generate_ids_for_manifest(manifest)

    if number_of_errors > 0:
        return jsonify({'manifestId': manifest.manifest_id,
                        'number_of_errors': number_of_errors,
                        'validations': validation_results})

    return jsonify(manifest)
