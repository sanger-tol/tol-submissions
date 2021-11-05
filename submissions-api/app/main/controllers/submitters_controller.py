# SPDX-FileCopyrightText: 2021 Genome Research Ltd.
#
# SPDX-License-Identifier: MIT

from flask import jsonify, send_from_directory
from sqlalchemy import or_
from main.model import db, SubmissionsRole, \
    SubmissionsManifest, SubmissionsSample, SubmissionsUser
import main.manifest_utils as manifest_utils
import main.excel_utils as excel_utils
import connexion
import tempfile


def get_manifests():
    role = db.session.query(SubmissionsRole) \
        .filter(or_(SubmissionsRole.role == 'submitter', SubmissionsRole.role == 'admin')) \
        .filter(SubmissionsRole.user_id == connexion.context["user"]) \
        .one_or_none()
    if role is None:
        return jsonify({'detail': "User does not have permission to use this function"}), 403
    manifests = db.session.query(SubmissionsManifest) \
        .order_by(SubmissionsManifest.manifest_id.desc()) \
        .all()

    return jsonify([manifest.to_dict_short() for manifest in manifests])


def upload_manifest_json(body={}, excel_file=None):  # noqa: E501
    role = db.session.query(SubmissionsRole) \
        .filter(or_(SubmissionsRole.role == 'submitter', SubmissionsRole.role == 'admin')) \
        .filter(SubmissionsRole.user_id == connexion.context["user"]) \
        .one_or_none()
    if role is None:
        return jsonify({'detail': "User does not have permission to use this function"}), 403
    user = db.session.query(SubmissionsUser) \
        .filter(SubmissionsUser.user_id == connexion.context["user"]) \
        .one_or_none()

    manifest = manifest_utils.create_manifest_from_json(body, user)
    db.session.add(manifest)
    db.session.commit()
    return(jsonify(manifest))


def upload_manifest_excel(excel_file=None, project_name=None):  # noqa: E501
    role = db.session.query(SubmissionsRole) \
        .filter(or_(SubmissionsRole.role == 'submitter', SubmissionsRole.role == 'admin')) \
        .filter(SubmissionsRole.user_id == connexion.context["user"]) \
        .one_or_none()
    if role is None:
        return jsonify({'detail': "User does not have permission to use this function"}), 403

    user = db.session.query(SubmissionsUser) \
        .filter(SubmissionsUser.user_id == connexion.context["user"]) \
        .one_or_none()
    uploaded_file = connexion.request.files['excelFile']

    # Save to a temporary location
    dir = tempfile.TemporaryDirectory()
    uploaded_file.save(dir.name+'/manifest.xlsx')

    # Do the validation
    manifest = excel_utils.read_excel(dirname=dir.name,
                                      filename='manifest.xlsx',
                                      user=user,
                                      project_name=project_name)

    # Quickly check for required fields - reject if any missing
    number_of_errors, validation_results = manifest_utils.validate_manifest(manifest, full=False)
    if number_of_errors > 0:
        return(jsonify({'manifestId': manifest.manifest_id,
                        'number_of_errors': number_of_errors,
                        'validations': validation_results}), 400)

    # Passed the basic checks so save it
    db.session.add(manifest)
    db.session.commit()

    # Save the manifest Excel file for returning at a later date
    excel_utils.save_excel(dirname=dir.name,
                           filename='manifest.xlsx',
                           manifest=manifest)
    db.session.commit()

    # Remove old file
    dir.cleanup()

    return jsonify(manifest)


def get_manifest(manifest_id=None):
    role = db.session.query(SubmissionsRole) \
        .filter(or_(SubmissionsRole.role == 'submitter', SubmissionsRole.role == 'admin')) \
        .filter(SubmissionsRole.user_id == connexion.context["user"]) \
        .one_or_none()
    if role is None:
        return jsonify({'detail': "User does not have permission to use this function"}), 403

    # Does the manifest exist?
    manifest = db.session.query(SubmissionsManifest) \
        .filter(SubmissionsManifest.manifest_id == manifest_id) \
        .one_or_none()
    if manifest is None:
        return jsonify({'detail': "Manifest does not exist"}), 404

    return(jsonify(manifest))


def validate_manifest(manifest_id=None):
    # Do the validation here
    role = db.session.query(SubmissionsRole) \
        .filter(or_(SubmissionsRole.role == 'submitter', SubmissionsRole.role == 'admin')) \
        .filter(SubmissionsRole.user_id == connexion.context["user"]) \
        .one_or_none()
    if role is None:
        return jsonify({'detail': "User does not have permission to use this function"}), 403

    # Does the manifest exist?
    manifest = db.session.query(SubmissionsManifest) \
        .filter(SubmissionsManifest.manifest_id == manifest_id) \
        .one_or_none()
    if manifest is None:
        return jsonify({'detail': "Manifest does not exist"}), 404

    number_of_errors, validation_results = manifest_utils.validate_manifest(manifest)
    return(jsonify({'manifestId': manifest.manifest_id,
                    'number_of_errors': number_of_errors,
                    'validations': validation_results}))


def submit_and_validate_manifest_json(body=None):
    role = db.session.query(SubmissionsRole) \
        .filter(or_(SubmissionsRole.role == 'submitter', SubmissionsRole.role == 'admin')) \
        .filter(SubmissionsRole.user_id == connexion.context["user"]) \
        .one_or_none()
    if role is None:
        return jsonify({'detail': "User does not have permission to use this function"}), 403

    user = db.session.query(SubmissionsUser) \
        .filter(SubmissionsUser.user_id == connexion.context["user"]) \
        .one_or_none()

    # Add the manifest
    manifest = manifest_utils.create_manifest_from_json(body, user)

    db.session.add(manifest)
    db.session.commit()

    # Validate the manifest
    number_of_errors, validation_results = manifest_utils.validate_manifest(manifest)
    return(jsonify({'manifestId': manifest.manifest_id,
                    'number_of_errors': number_of_errors,
                    'validations': validation_results}))


def generate_ids_for_manifest(manifest_id=None):
    # Do the validation here
    role = db.session.query(SubmissionsRole) \
        .filter(or_(SubmissionsRole.role == 'submitter', SubmissionsRole.role == 'admin')) \
        .filter(SubmissionsRole.user_id == connexion.context["user"]) \
        .one_or_none()
    if role is None:
        return jsonify({'detail': "User does not have permission to use this function"}), 403

    # Does the manifest exist?
    manifest = db.session.query(SubmissionsManifest) \
        .filter(SubmissionsManifest.manifest_id == manifest_id) \
        .one_or_none()
    if manifest is None:
        return jsonify({'detail': "Manifest does not exist"}), 404

    number_of_errors, validation_results = manifest_utils.generate_ids_for_manifest(manifest)

    if number_of_errors > 0:
        return(jsonify({'manifestId': manifest.manifest_id,
                        'number_of_errors': number_of_errors,
                        'validations': validation_results}))

    return(jsonify(manifest))


def submit_and_generate_manifest_json(body=None):
    role = db.session.query(SubmissionsRole) \
        .filter(or_(SubmissionsRole.role == 'submitter', SubmissionsRole.role == 'admin')) \
        .filter(SubmissionsRole.user_id == connexion.context["user"]) \
        .one_or_none()
    if role is None:
        return jsonify({'detail': "User does not have permission to use this function"}), 403

    user = db.session.query(SubmissionsUser) \
        .filter(SubmissionsUser.user_id == connexion.context["user"]) \
        .one_or_none()

    # Add the manifest
    manifest = manifest_utils.create_manifest_from_json(body, user)

    db.session.add(manifest)
    db.session.commit()

    number_of_errors, validation_results = manifest_utils.generate_ids_for_manifest(manifest)

    if number_of_errors > 0:
        return(jsonify({'manifestId': manifest.manifest_id,
                        'number_of_errors': number_of_errors,
                        'validations': validation_results}))

    return(jsonify(manifest))


def download_manifest_excel(manifest_id=None):
    role = db.session.query(SubmissionsRole) \
        .filter(or_(SubmissionsRole.role == 'submitter', SubmissionsRole.role == 'admin')) \
        .filter(SubmissionsRole.user_id == connexion.context["user"]) \
        .one_or_none()
    if role is None:
        return jsonify({'detail': "User does not have permission to use this function"}), 403

    # Does the manifest exist?
    manifest = db.session.query(SubmissionsManifest) \
        .filter(SubmissionsManifest.manifest_id == manifest_id) \
        .one_or_none()
    if manifest is None:
        return jsonify({'detail': "Manifest does not exist"}), 404

    # Bring out of S3
    dir = tempfile.TemporaryDirectory()
    filename = "manifest.xlsx"
    if not excel_utils.load_excel(manifest=manifest, dirname=dir.name, filename=filename):
        # This manifest was not loaded by Excel - create an Excel file
        excel_utils.create_excel(manifest=manifest, dirname=dir.name, filename=filename)

    # Add the columns
    excel_utils.add_columns(manifest=manifest, fields=SubmissionsSample.id_fields,
                            dirname=dir.name, filename=filename)

    # Stream out the Excel file
    return send_from_directory(dir.name, filename=filename,
                               as_attachment=True)
