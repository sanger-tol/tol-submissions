from flask import jsonify
from sqlalchemy import or_
from swagger_server.model import db, SubmissionsRole, \
    SubmissionsManifest, SubmissionsUser
import swagger_server.manifest_utils as manifest_utils
import connexion


def submit_manifest_json(body=None):  # noqa: E501
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
