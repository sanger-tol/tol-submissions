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

    manifest = SubmissionsManifest()
    db.session.add(manifest)
    for s in body['samples']:
        sample = SubmissionsSample()
        sample.manifest = manifest
        sample.row = s.get('row')
        sample.specimen_id = s.get('SPECIMEN_ID')
        sample.taxonomy_id = s.get('TAXON_ID')
        sample.scientific_name = s.get('SCIENTIFIC_NAME')
        sample.common_name = s.get('COMMON_NAME')
        sample.lifestage = s.get('LIFESTAGE')
        sample.sex = s.get('SEX')
        sample.organism_part = s.get('ORGANISM_PART')
        sample.GAL = s.get('GAL')
        sample.GAL_sample_id = s.get('GAL_SAMPLE_ID')
        sample.collected_by = s.get('COLLECTED_BY')
        sample.collector_affiliation = s.get('COLLECTOR_AFFILIATION')
        sample.date_of_collection = s.get('DATE_OF_COLLECTION')
        sample.collection_location = s.get('COLLECTION_LOCATION')
        sample.decimal_latitude = s.get('DECIMAL_LATITUDE')
        sample.decimal_longitude = s.get('DECIMAL_LONGITUDE')
        sample.habitat = s.get('HABITAT')
        sample.identified_by = s.get('IDENTIFIED_BY')
        sample.identifier_affiliation = s.get('IDENTIFIER_AFFILIATION')
        sample.voucher_id = s.get('VOUCHER_ID')
        sample.elevation = s.get('ELEVATION')
        sample.depth = s.get('DEPTH')
        sample.relationship = s.get('RELATIONSHIP')
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
