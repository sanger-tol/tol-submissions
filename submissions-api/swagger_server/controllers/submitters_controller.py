from flask import jsonify, send_from_directory
from sqlalchemy import or_
from swagger_server.model import db, SubmissionsRole
import connexion
import tempfile


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
