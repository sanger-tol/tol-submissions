from flask import jsonify, send_from_directory
from sqlalchemy import or_
from swagger_server.model import db, SubmissionsRole, \
    SubmissionsManifest, SubmissionsSample
import connexion
import tempfile


def submit_manifest_json(body=None):  # noqa: E501
    role = db.session.query(SubmissionsRole) \
        .filter(or_(SubmissionsRole.role == 'submitter', SubmissionsRole.role == 'admin')) \
        .filter(SubmissionsRole.user_id == connexion.context["user"]) \
        .one_or_none()
    if role is None:
        return jsonify({'detail': "User does not have permission to use this function"}), 403

    manifest = db.session.query(SubmissionsManifest) \
        .filter(SubmissionsManifest.manifest_id == body["manifestId"]) \
        .one_or_none()
    if manifest is not None:
        return jsonify({'detail': "Manifest already exists"}), 400

    manifest = SubmissionsManifest()
    manifest.manifest_id = body['manifestId']
    db.session.add(manifest)
    for s in body['samples']:
        sample = SubmissionsSample()
        sample.manifest = manifest
        sample.sample_id = s['sampleId']
        sample.taxonomy_id = s['taxonomyId']
        sample.specimen_id = s['specimenId']
        # The following are the optional fields
        sample.scientific_name = s.get('scientificName')
        sample.common_name = s.get('commonName')
        sample.lifestage = s.get('lifestage')
        sample.sex = s.get('sex')
        sample.organism_part = s.get('organismPart')
        sample.GAL = s.get('GAL')
        sample.GAL_sample_id = s.get('GALSampleId')
        sample.collected_by = s.get('collectedBy')
        sample.collector_affiliation = s.get('collectorAffiliation')
        sample.date_of_collection = s.get('dateOfCollection')
        sample.collection_location = s.get('collectionLocation')
        sample.decimal_latitude = s.get('decimalLatitude')
        sample.decimal_longitude = s.get('decimalLongitude')
        sample.habitat = s.get('habitat')
        sample.identified_by = s.get('identifiedBy')
        sample.identifier_affiliation = s.get('identifierAffiliation')
        sample.voucher_id = s.get('voucherId')
        db.session.add(sample)
        # The following are not added here
        # biosampleId
        # tolId
    db.session.commit()
    return(jsonify(manifest))


def submit_manifest(excel_file=None):  # noqa: E501
    role = db.session.query(SubmissionsRole) \
        .filter(or_(SubmissionsRole.role == 'submitter', SubmissionsRole.role == 'admin')) \
        .filter(SubmissionsRole.user_id == connexion.context["user"]) \
        .one_or_none()
    if role is None:
        return jsonify({'detail': "User does not have permission to use this function"}), 403

    uploaded_file = connexion.request.files['excelFile']

    # Save to a temporary location
    dir = tempfile.TemporaryDirectory()
    uploaded_file.save(dir.name+'/manifest.xlsx')

    # Do the submission
    # This is where the call to the COPO code needs to go
    submitted = False
    updated_filename = uploaded_file.name
    errors = []

    if submitted:
        # Stream out the validated Excel file and remove
        return send_from_directory(dir.name, filename=updated_filename,
                                   as_attachment=True)
    else:
        # Return the error
        return jsonify({"errors": errors}), 400

    # Remove old file
    dir.cleanup()
