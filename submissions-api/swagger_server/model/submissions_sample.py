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
    common_name = db.Column(db.String(), nullable=True)
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
    biosample_accession = db.Column(db.String(), nullable=True)
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
                'biosampleAccession': cls.biosample_accession,
                'sraAccession': cls.sra_accession,
                'submissionAccession': cls.submission_accession,
                'submissionError': cls.submission_error,
                'sampleSameAs': cls.sample_same_as,
                'sampleDerivedFrom': cls.sample_derived_from,
                'sampleSymbiontOf': cls.sample_symbiont_of}

    def to_ena_dict(cls):
        # Listed in the order they appear on the ENA checklist
        ret = {"ENA-CHECKLIST": {"value": "ERC000053"}}
        ret["organism part"] = {"value": cls.organism_part.replace("_", " ")}
        ret["lifestage"] = {
            "value": "spore-bearing structure" if cls.lifestage == "SPORE_BEARING_STRUCTURE"
            else cls.lifestage.replace("_", " ")}
        ret["project name"] = {"value": cls.manifest.project_name}
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

    all_fields = [{"python_name": "specimen_id",
                   "field_name": "SPECIMEN_ID",
                   "required": True},
                  {"python_name": "taxonomy_id",
                   "field_name": "TAXON_ID",
                   "required": True},
                  {"python_name": "scientific_name",
                   "field_name": "SCIENTIFIC_NAME",
                   "required": True},
                  {"python_name": "family",
                   "field_name": "FAMILY",
                   "required": True},
                  {"python_name": "genus",
                   "field_name": "GENUS",
                   "required": True},
                  {"python_name": "order_or_group",
                   "field_name": "ORDER_OR_GROUP",
                   "required": True},
                  {"python_name": "common_name",
                   "field_name": "COMMON_NAME",
                   "required": False},
                  {"python_name": "lifestage",
                   "field_name": "LIFESTAGE",
                   "required": True},
                  {"python_name": "sex",
                   "field_name": "SEX",
                   "required": True},
                  {"python_name": "organism_part",
                   "field_name": "ORGANISM_PART",
                   "required": True},
                  {"python_name": "GAL",
                   "field_name": "GAL",
                   "required": True},
                  {"python_name": "GAL_sample_id",
                   "field_name": "GAL_SAMPLE_ID",
                   "required": True},
                  {"python_name": "collected_by",
                   "field_name": "COLLECTED_BY",
                   "required": True},
                  {"python_name": "collector_affiliation",
                   "field_name": "COLLECTOR_AFFILIATION",
                   "required": True},
                  {"python_name": "date_of_collection",
                   "field_name": "DATE_OF_COLLECTION",
                   "required": True},
                  {"python_name": "collection_location",
                   "field_name": "COLLECTION_LOCATION",
                   "required": True},
                  {"python_name": "decimal_latitude",
                   "field_name": "DECIMAL_LATITUDE",
                   "required": True},
                  {"python_name": "decimal_longitude",
                   "field_name": "DECIMAL_LONGITUDE",
                   "required": True},
                  {"python_name": "habitat",
                   "field_name": "HABITAT",
                   "required": True},
                  {"python_name": "identified_by",
                   "field_name": "IDENTIFIED_BY",
                   "required": True},
                  {"python_name": "identifier_affiliation",
                   "field_name": "IDENTIFIER_AFFILIATION",
                   "required": True},
                  {"python_name": "voucher_id",
                   "field_name": "VOUCHER_ID",
                   "required": True},
                  {"python_name": "elevation",
                   "field_name": "ELEVATION",
                   "required": False},
                  {"python_name": "depth",
                   "field_name": "DEPTH",
                   "required": False},
                  {"python_name": "relationship",
                   "field_name": "RELATIONSHIP",
                   "required": False},
                  {"python_name": "symbiont",
                   "field_name": "SYMBIONT",
                   "required": False},
                  {"python_name": "culture_or_strain_id",
                   "field_name": "CULTURE_OR_STRAIN_ID",
                   "required": False}]

    id_fields = [{"python_name": "tolid",
                  "field_name": "PUBLIC_NAME",
                  "required": True},
                 {"python_name": "sample_same_as",
                  "field_name": "SAMPLE_SAME_AS",
                  "required": True},
                 {"python_name": "sample_derived_from",
                  "field_name": "SAMPLE_DERIVED_FROM",
                  "required": True},
                 {"python_name": "sample_symbiont_of",
                  "field_name": "SAMPLE_SYMBIONT_OF",
                  "required": True},
                 {"python_name": "biosample_accession",
                  "field_name": "BIOSAMPLE_ACCESSION",
                  "required": True},
                 {"python_name": "sra_accession",
                  "field_name": "SRA_ACCESSION",
                  "required": True},
                 {"python_name": "submission_accession",
                  "field_name": "SUBMISSION_ACCESSION",
                  "required": True}]
