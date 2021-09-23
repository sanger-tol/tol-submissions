from flask import jsonify
from sqlalchemy import or_
from swagger_server.model import db, SubmissionsSample
from swagger_server.specimen_utils import get_specimen_sts, get_biospecimen_sts


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
        "specimenId": specimen.specimen_id,
        "biospecimenId": biosspecimen_id,
        "samples": samples,
    })


def get_samples_by_specimen_id(specimen_id):
    # Does the specimen exist?
    specimen = get_specimen_sts(specimen_id)
    if specimen is None:
        return jsonify({'detail': "Specimen does not exist"}), 404

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
        return jsonify({'detail': "Specimen does not exist"}), 404

    # return the samples
    return get_samples_from_specimen(specimen)


def get_sample(biosample_id):
    # Does the sample exist?
    sample = db.session.query(SubmissionsSample) \
        .filter(SubmissionsSample.biosample_accession == biosample_id) \
        .one_or_none()
    if sample is None:
        return jsonify({'detail': "Sample does not exist"}), 404

    return jsonify(sample)
