from .base import Base, db


class SubmissionsSample(Base):
    __tablename__ = "sample"
    sample_id = db.Column(db.String(), primary_key=True)
    taxonomy_id = db.Column(db.Integer, nullable=False)
    scientific_name = db.Column(db.String(), nullable=True)
    common_name = db.Column(db.String(), nullable=True)
    specimen_id = db.Column(db.String(), nullable=False)
    biosample_id = db.Column(db.String(), nullable=True)
    manifest_id = db.Column(db.String(), db.ForeignKey('manifest.manifest_id'))
    manifest = db.relationship("SubmissionsManifest", back_populates="samples",
                               uselist=False, foreign_keys=[manifest_id])
    lifestage = db.Column(db.String(), nullable=True)
    sex = db.Column(db.String(), nullable=True)
    organism_part = db.Column(db.String(), nullable=True)
    GAL = db.Column(db.String(), nullable=True)
    GAL_sample_id = db.Column(db.String(), nullable=True)
    collected_by = db.Column(db.String(), nullable=True)
    collector_affiliation = db.Column(db.String(), nullable=True)
    date_of_collection = db.Column(db.String(), nullable=True)
    collection_location = db.Column(db.String(), nullable=True)
    decimal_latitude = db.Column(db.String(), nullable=True)
    decimal_longitude = db.Column(db.String(), nullable=True)
    habitat = db.Column(db.String(), nullable=True)
    identified_by = db.Column(db.String(), nullable=True)
    identifier_affiliation = db.Column(db.String(), nullable=True)
    voucher_id = db.Column(db.String(), nullable=True)
    tolid = db.Column(db.String(), nullable=True)

    def to_dict(cls):
        return {'sampleId': cls.sample_id,
                'taxonomyId': cls.taxonomy_id,
                'scientificName': cls.scientific_name,
                'commonName': cls.common_name,
                'specimenId': cls.specimen_id,
                'biosampleId': cls.biosample_id,
                'lifestage': cls.lifestage,
                'sex': cls.sex,
                'organismPart': cls.organism_part,
                'GAL': cls.GAL,
                'GALSampleId': cls.GAL_sample_id,
                'collectedBy': cls.collected_by,
                'collectorAffiliation': cls.collector_affiliation,
                'dateOfCollection': cls.date_of_collection,
                'collectionLocation': cls.collection_location,
                'decimalLatitude': cls.decimal_latitude,
                'decimalLongitude': cls.decimal_longitude,
                'habitat': cls.habitat,
                'identifiedBy': cls.identified_by,
                'identifierAffiliation': cls.identifier_affiliation,
                'voucherId': cls.voucher_id,
                'tolId': cls.tolid}
