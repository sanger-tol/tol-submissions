from .base import Base, db


class SubmissionsSample(Base):
    __tablename__ = "sample"
    row = db.Column(db.Integer, nullable=False)
    specimen_id = db.Column(db.String(), nullable=False)
    sample_id = db.Column(db.Integer, primary_key=True)
    taxonomy_id = db.Column(db.Integer, nullable=False)
    scientific_name = db.Column(db.String(), nullable=False)
    family = db.Column(db.String(), nullable=False)
    genus = db.Column(db.String(), nullable=False)
    order_or_group = db.Column(db.String(), nullable=False)
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
    symbiont = db.Column(db.String(), nullable=True)
    culture_or_strain_id = db.Column(db.String(), nullable=True)

    tolid = db.Column(db.String(), nullable=True)
    biosample_id = db.Column(db.String(), nullable=True)
    sra_accession = db.Column(db.String(), nullable=True)
    submission_accession = db.Column(db.String(), nullable=True)
    submission_error = db.Column(db.String(), nullable=True)

    sample_same_as = db.Column(db.String(), nullable=True)
    sample_derived_from = db.Column(db.String(), nullable=True)
    sample_symbiont_of = db.Column(db.String(), nullable=True)

    def collection_country(self):
        return self.collection_location.split(' | ')[0]

    def collection_region(self):
        return ' | '.join(self.collection_location.split(' | ')[1:])

    def to_dict(cls):
        return {'row': cls.row,
                'SPECIMEN_ID': cls.specimen_id,
                'TAXON_ID': cls.taxonomy_id,
                'SCIENTIFIC_NAME': cls.scientific_name,
                'FAMILY': cls.family,
                'GENUS': cls.genus,
                'ORDER_OR_GROUP': cls.order_or_group,
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
                'SYMBIONT': cls.symbiont,
                'CULTURE_OR_STRAIN_ID': cls.culture_or_strain_id,
                'tolId': cls.tolid,
                'biosampleId': cls.biosample_id,
                'sraAccession': cls.sra_accession,
                'submissionAccession': cls.submission_accession,
                'submissionError': cls.submission_error}

    def to_ena_dict(cls):
        # Listed in the order they appear on the ENA checklist
        ret = {"ENA-CHECKLIST": {"value": "ERC000053"}}
        ret["organism part"] = {"value": cls.organism_part.replace("_", " ")}
        ret["lifestage"] = {
            "value": "spore-bearing structure" if cls.lifestage == "SPORE_BEARING_STRUCTURE"
            else cls.lifestage.replace("_", " ")}
        ret["project name"] = {"value": "TOL"}
        ret["tolid"] = {"value": cls.tolid}
        ret["collected by"] = {"value": cls.collected_by.replace("_", " ")}
        ret["collection date"] = {"value": cls.date_of_collection}
        ret["geographic location (country and/or sea)"] = {
            "value": cls.collection_country().replace("_", " ")}
        ret["geographic location (latitude)"] = {"value": cls.decimal_latitude,
                                                 "units": "DD"}
        ret["geographic location (longitude)"] = {"value": cls.decimal_longitude,
                                                  "units": "DD"}
        ret["geographic location (region and locality)"] = {
            "value": cls.collection_region().replace("_", " ")}
        ret["identified_by"] = {"value": cls.identified_by.replace("_", " ")}
        if cls.depth is not None:
            ret["geographic location (depth)"] = {"value": cls.depth,
                                                  "units": "m"}
        if cls.elevation is not None:
            ret["geographic location (elevation)"] = {"value": cls.elevation,
                                                      "units": "m"}
        ret["habitat"] = {"value": cls.habitat.replace("_", " ")}
        ret["identifier_affiliation"] = {"value": cls.identifier_affiliation.replace("_", " ")}
        if cls.sample_derived_from is not None:
            ret["sample derived from"] = {"value": cls.sample_derived_from}
        if cls.sample_same_as is not None:
            ret["sample same as"] = {"value": cls.sample_same_as}
        if cls.sample_symbiont_of is not None:
            ret["sample symbiont of"] = {"value": cls.sample_symbiont_of}
        ret["sex"] = {"value": cls.sex.replace("_", " ")}
        if cls.relationship is not None:
            ret["relationship"] = {"value": cls.relationship.replace("_", " ")}
        if cls.symbiont is not None:
            ret["symbiont"] = {"value": cls.symbiont.replace("_", " ")}
        ret["collecting institution"] = {"value": cls.collector_affiliation.replace("_", " ")}
        ret["GAL"] = {"value": cls.GAL.replace("_", " ")}
        ret["specimen_voucher"] = {"value": cls.voucher_id.replace("_", " ")}
        ret["specimen_id"] = {"value": cls.specimen_id.replace("_", " ")}
        ret["GAL_sample_id"] = {"value": cls.GAL_sample_id.replace("_", " ")}
        if cls.culture_or_strain_id is not None:
            ret["culture_or_strain_id"] = {"value": cls.culture_or_strain_id.replace("_", " ")}
        return ret
