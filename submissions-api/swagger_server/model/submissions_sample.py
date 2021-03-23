from .base import Base, db


class SubmissionsSample(Base):
    __tablename__ = "sample"
    row = db.Column(db.Integer, nullable=False)
    specimen_id = db.Column(db.String(), nullable=False)
    sample_id = db.Column(db.Integer, primary_key=True)
    taxonomy_id = db.Column(db.Integer, nullable=False)
    scientific_name = db.Column(db.String(), nullable=False)
    common_name = db.Column(db.String(), nullable=False)
    manifest_id = db.Column(db.Integer, db.ForeignKey('manifest.manifest_id'))
    manifest = db.relationship("SubmissionsManifest", back_populates="samples",
                               uselist=False, foreign_keys=[manifest_id])
    lifestage = db.Column(db.String(), nullable=False)
    sex = db.Column(db.String(), nullable=False)
    organism_part = db.Column(db.String(), nullable=False)
    GAL = db.Column(db.String(), nullable=False)
    GAL_sample_id = db.Column(db.String(), nullable=False)
    collected_by = db.Column(db.String(), nullable=False)
    collector_affiliation = db.Column(db.String(), nullable=False)
    date_of_collection = db.Column(db.String(), nullable=False)
    collection_location = db.Column(db.String(), nullable=False)
    decimal_latitude = db.Column(db.String(), nullable=False)
    decimal_longitude = db.Column(db.String(), nullable=False)
    habitat = db.Column(db.String(), nullable=False)
    identified_by = db.Column(db.String(), nullable=False)
    identifier_affiliation = db.Column(db.String(), nullable=False)
    voucher_id = db.Column(db.String(), nullable=False)
    elevation = db.Column(db.String(), nullable=True)
    depth = db.Column(db.String(), nullable=True)
    relationship = db.Column(db.String(), nullable=True)

    tolid = db.Column(db.String(), nullable=True)
    biosample_id = db.Column(db.String(), nullable=True)

    def to_dict(cls):
        return {'row': cls.row,
                'SPECIMEN_ID': cls.specimen_id,
                'TAXON_ID': cls.taxonomy_id,
                'SCIENTIFIC_NAME': cls.scientific_name,
                'COMMON_NAME': cls.common_name,
                'LIFESTAGE': cls.lifestage,
                'SEX': cls.sex,
                'ORGANISM_PART': cls.organism_part,
                'GAL': cls.GAL,
                'GAL_SAMPLE_ID': cls.GAL_sample_id,
                'COLLECTED_BY': cls.collected_by,
                'COLLECTOR_AFFILIATION': cls.collector_affiliation,
                'DATE_OF_COLLECTION': cls.date_of_collection,
                'COLLECTION_LOCATION': cls.collection_location,
                'DECIMAL_LATITUDE': cls.decimal_latitude,
                'DECIMAL_LONGITUDE': cls.decimal_longitude,
                'HABITAT': cls.habitat,
                'IDENTIFIED_BY': cls.identified_by,
                'IDENTIFIER_AFFILIATION': cls.identifier_affiliation,
                'VOUCHER_ID': cls.voucher_id,
                'ELEVATION': cls.elevation,
                'DEPTH': cls.depth,
                'RELATIONSHIP': cls.relationship,
                'tolId': cls.tolid,
                'biosampleId': cls.biosample_id}
