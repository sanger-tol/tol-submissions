from .base import Base, db
import re


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
    other_information = db.Column(db.String(), nullable=True)
    elevation = db.Column(db.String(), nullable=True)
    depth = db.Column(db.String(), nullable=True)
    relationship = db.Column(db.String(), nullable=True)
    symbiont = db.Column(db.String(), nullable=True)
    culture_or_strain_id = db.Column(db.String(), nullable=True)
    series = db.Column(db.String(), nullable=True)
    rack_or_plate_id = db.Column(db.String(), nullable=True)
    tube_or_well_id = db.Column(db.String(), nullable=True)
    taxon_remarks = db.Column(db.String(), nullable=True)
    infraspecific_epithet = db.Column(db.String(), nullable=True)
    collector_sample_id = db.Column(db.String(), nullable=True)
    grid_reference = db.Column(db.String(), nullable=True)
    time_of_collection = db.Column(db.String(), nullable=True)
    description_of_collection_method = db.Column(db.String(), nullable=True)
    difficult_or_high_priority_sample = db.Column(db.String(), nullable=True)
    identified_how = db.Column(db.String(), nullable=True)
    specimen_id_risk = db.Column(db.String(), nullable=True)
    preserved_by = db.Column(db.String(), nullable=True)
    preserver_affiliation = db.Column(db.String(), nullable=True)
    preservation_approach = db.Column(db.String(), nullable=True)
    preservative_solution = db.Column(db.String(), nullable=True)
    time_elapsed_from_collection_to_preservation = db.Column(db.String(), nullable=True)
    date_of_preservation = db.Column(db.String(), nullable=True)
    size_of_tissue_in_tube = db.Column(db.String(), nullable=True)
    tissue_removed_for_barcoding = db.Column(db.String(), nullable=True)
    plate_id_for_barcoding = db.Column(db.String(), nullable=True)
    tube_or_well_id_for_barcoding = db.Column(db.String(), nullable=True)
    tissue_for_barcoding = db.Column(db.String(), nullable=True)
    barcode_plate_preservative = db.Column(db.String(), nullable=True)
    purpose_of_specimen = db.Column(db.String(), nullable=True)
    hazard_group = db.Column(db.String(), nullable=True)
    regulatory_compliance = db.Column(db.String(), nullable=True)
    original_collection_date = db.Column(db.String(), nullable=True)
    original_geographic_location = db.Column(db.String(), nullable=True)
    barcode_hub = db.Column(db.String(), nullable=True)

    tolid = db.Column(db.String(), nullable=True)
    biosample_accession = db.Column(db.String(), nullable=True)
    sra_accession = db.Column(db.String(), nullable=True)
    submission_accession = db.Column(db.String(), nullable=True)
    submission_error = db.Column(db.String(), nullable=True)

    sample_same_as = db.Column(db.String(), nullable=True)
    sample_derived_from = db.Column(db.String(), nullable=True)
    sample_symbiont_of = db.Column(db.String(), nullable=True)

    sample_fields = db.relationship('SubmissionsSampleField', back_populates="sample",
                                    lazy=False, order_by='SubmissionsSampleField.name')

    def collection_country(self):
        return re.split(r'\s*\|\s*', self.collection_location)[0]

    def collection_region(self):
        return ' | '.join(re.split(r'\s*\|\s*', self.collection_location)[1:])

    def to_dict(cls):
        return {**{'row': cls.row},
                **{field["field_name"]: getattr(cls, field["python_name"])
                    for field in cls.all_fields},
                **{field["field_name"]: getattr(cls, field["python_name"])
                    for field in cls.id_fields},
                **{field.name: field.value for field in cls.sample_fields}}

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
        ret["geographic location (latitude)"] = {"value": cls.decimal_latitude.replace("_", " ").lower(),  # noqa
                                                 "units": "DD"}
        ret["geographic location (longitude)"] = {"value": cls.decimal_longitude.replace("_", " ").lower(),  # noqa
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
        if cls.original_collection_date is not None:
            ret["original collection date"] = {"value": cls.original_collection_date}
        if cls.original_geographic_location is not None:
            ret["original geographic location"] = {"value": cls.original_geographic_location.replace("_", " ")}  # noqa
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
            ret["symbiont"] = {"value": "Y" if cls.symbiont == "SYMBIONT" else "N"}
        ret["collecting institution"] = {"value": cls.collector_affiliation.replace("_", " ")}
        ret["GAL"] = {"value": cls.GAL.replace("_", " ")}
        ret["specimen_voucher"] = {"value": cls.voucher_id.replace("_", " ")}
        ret["specimen_id"] = {"value": cls.specimen_id.replace("_", " ")}
        ret["GAL_sample_id"] = {"value": cls.GAL_sample_id.replace("_", " ")}
        if cls.culture_or_strain_id is not None:
            ret["culture_or_strain_id"] = {"value": cls.culture_or_strain_id.replace("_", " ")}
        return ret

    def is_symbiont(cls):
        if cls.symbiont is not None:
            if cls.symbiont == "SYMBIONT":
                return True
        return False

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
                   "field_name": "LIFESTAGE",  # Validated in ENA checklist
                   "required": True},
                  {"python_name": "sex",
                   "field_name": "SEX",
                   "required": True,
                   "allowed_values": ["FEMALE", "MALE", "HERMAPHRODITE_MONOECIOUS",
                                      "NOT_COLLECTED", "NOT_APPLICABLE", "NOT_PROVIDED",
                                      "ASEXUAL_MORPH", "SEXUAL_MORPH"]},
                  {"python_name": "organism_part",
                   "field_name": "ORGANISM_PART",
                   "required": True,
                   "split_pattern": r'\s*\|\s*',
                   "allowed_values": ["WHOLE_ORGANISM", "HEAD", "THORAX", "ABDOMEN",
                                      "CEPHALOTHORAX", "BRAIN", "EYE", "FAT_BODY", "INTESTINE",
                                      "BODYWALL", "TERMINAL_BODY", "ANTERIOR_BODY", "MID_BODY",
                                      "POSTERIOR_BODY", "HEPATOPANCREAS", "LEG", "BLOOD", "LUNG",
                                      "HEART", "KIDNEY", "LIVER", "ENDOCRINE_TISSUE", "SPLEEN",
                                      "STOMACH", "PANCREAS", "MUSCLE", "MODULAR_COLONY",
                                      "TENTACLE", "FIN", "SKIN", "SCAT", "EGGSHELL", "SCALES",
                                      "HAIR", "GILL_ANIMAL", "**OTHER_SOMATIC_ANIMAL_TISSUE**",
                                      "OVIDUCT", "GONAD", "OVARY_ANIMAL", "TESTIS",
                                      "SPERM_SEMINAL_FLUID", "EGG",
                                      "**OTHER_REPRODUCTIVE_ANIMAL_TISSUE**", "WHOLE_PLANT",
                                      "SEEDLING", "SEED", "LEAF", "FLOWER", "BLADE", "STEM",
                                      "PETIOLE", "SHOOT", "BUD", "THALLUS_PLANT", "BRACT",
                                      "**OTHER_PLANT_TISSUE**", "MYCELIUM", "MYCORRHIZA",
                                      "SPORE_BEARING_STRUCTURE", "HOLDFAST_FUNGI", "STIPE",
                                      "CAP", "GILL_FUNGI", "THALLUS_FUNGI", "SPORE",
                                      "**OTHER_FUNGAL_TISSUE**", "NOT_COLLECTED",
                                      "NOT_APPLICABLE", "NOT_PROVIDED", "MOLLUSC_FOOT",
                                      "UNICELLULAR_ORGANISMS_IN_CULTURE",
                                      "MULTICELLULAR_ORGANISMS_IN_CULTURE"]},
                  {"python_name": "GAL",
                   "field_name": "GAL",  # Validated in ENA checklist
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
                  {"python_name": "other_information",
                   "field_name": "OTHER_INFORMATION",
                   "required": False},
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
                   "required": False,
                   "allowed_values": ['TARGET', 'SYMBIONT']},
                  {"python_name": "culture_or_strain_id",
                   "field_name": "CULTURE_OR_STRAIN_ID",
                   "required": False},
                  {"python_name": "series",
                   "field_name": "SERIES",
                   "required": False,
                   "error_regex": r'^\d+$'},
                  {"python_name": "rack_or_plate_id",
                   "field_name": "RACK_OR_PLATE_ID",
                   "required": False,
                   "warning_regex": r'^[a-zA-Z]{2}\d{8}$'},
                  {"python_name": "tube_or_well_id",
                   "field_name": "TUBE_OR_WELL_ID",
                   "required": False,
                   "warning_regex": r'^[a-zA-Z]{2}\d{8}$'},
                  {"python_name": "taxon_remarks",
                   "field_name": "TAXON_REMARKS",
                   "required": False},
                  {"python_name": "infraspecific_epithet",
                   "field_name": "INFRASPECIFIC_EPITHET",
                   "required": False},
                  {"python_name": "collector_sample_id",
                   "field_name": "COLLECTOR_SAMPLE_ID",
                   "required": False},
                  {"python_name": "grid_reference",
                   "field_name": "GRID_REFERENCE",
                   "required": False},
                  {"python_name": "time_of_collection",
                   "field_name": "TIME_OF_COLLECTION",
                   "required": False,
                   "error_regex": r"^([0-1][0-9]|2[0-4]):[0-5]\d$"},
                  {"python_name": "description_of_collection_method",
                   "field_name": "DESCRIPTION_OF_COLLECTION_METHOD",
                   "required": False},
                  {"python_name": "difficult_or_high_priority_sample",
                   "field_name": "DIFFICULT_OR_HIGH_PRIORITY_SAMPLE",
                   "required": False,
                   "allowed_values": ["HIGH_PRIORITY", "DIFFICULT", "NOT_APPLICABLE",
                                      "NOT_PROVIDED", "NOT_COLLECTED", "FULL_CURATION"]},
                  {"python_name": "identified_how",
                   "field_name": "IDENTIFIED_HOW",
                   "required": False},
                  {"python_name": "specimen_id_risk",
                   "field_name": "SPECIMEN_ID_RISK",
                   "required": False,
                   "allowed_values": ["Y", "N"]},
                  {"python_name": "preserved_by",
                   "field_name": "PRESERVED_BY",
                   "required": False},
                  {"python_name": "preserver_affiliation",
                   "field_name": "PRESERVER_AFFILIATION",
                   "required": False},
                  {"python_name": "preservation_approach",
                   "field_name": "PRESERVATION_APPROACH",
                   "required": False},
                  {"python_name": "preservative_solution",
                   "field_name": "PRESERVATIVE_SOLUTION",
                   "required": False},
                  {"python_name": "time_elapsed_from_collection_to_preservation",
                   "field_name": "TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION",
                   "required": False,
                   "error_regex": r'^\d+|NOT_COLLECTED|NOT_PROVIDED|NOT_APPLICABLE$'},  # noqa
                  {"python_name": "date_of_preservation",
                   "field_name": "DATE_OF_PRESERVATION",
                   "required": False},
                  {"python_name": "size_of_tissue_in_tube",
                   "field_name": "SIZE_OF_TISSUE_IN_TUBE",
                   "required": False,
                   "allowed_values": ["VS", "S", "M", "L", "SINGLE_CELL", "NOT_COLLECTED",
                                      "NOT_APPLICABLE", "NOT_PROVIDED"]},
                  {"python_name": "tissue_removed_for_barcoding",
                   "field_name": "TISSUE_REMOVED_FOR_BARCODING",
                   "required": False,
                   "allowed_values": ["Y", "N", "NOT_COLLECTED", "NOT_APPLICABLE",
                                      "NOT_PROVIDED"]},
                  {"python_name": "plate_id_for_barcoding",
                   "field_name": "PLATE_ID_FOR_BARCODING",
                   "required": False},
                  {"python_name": "tube_or_well_id_for_barcoding",
                   "field_name": "TUBE_OR_WELL_ID_FOR_BARCODING",
                   "required": False},
                  {"python_name": "tissue_for_barcoding",
                   "field_name": "TISSUE_FOR_BARCODING",
                   "required": False,
                   "allowed_values": ["WHOLE_ORGANISM", "HEAD", "THORAX", "ABDOMEN",
                                      "CEPHALOTHORAX", "BRAIN", "EYE", "FAT_BODY", "INTESTINE",
                                      "BODYWALL", "TERMINAL_BODY", "ANTERIOR_BODY", "MID_BODY",
                                      "POSTERIOR_BODY", "HEPATOPANCREAS", "LEG", "BLOOD", "LUNG",
                                      "HEART", "KIDNEY", "LIVER", "ENDOCRINE_TISSUE", "SPLEEN",
                                      "STOMACH", "PANCREAS", "MUSCLE", "MODULAR_COLONY",
                                      "TENTACLE", "FIN", "SKIN", "SCAT", "EGGSHELL", "SCALES",
                                      "HAIR", "GILL_ANIMAL", "**OTHER_SOMATIC_ANIMAL_TISSUE**",
                                      "OVIDUCT", "GONAD", "OVARY_ANIMAL", "TESTIS",
                                      "SPERM_SEMINAL_FLUID", "EGG",
                                      "**OTHER_REPRODUCTIVE_ANIMAL_TISSUE**", "WHOLE_PLANT",
                                      "SEEDLING", "SEED", "LEAF", "FLOWER", "BLADE", "STEM",
                                      "PETIOLE", "SHOOT", "BUD", "THALLUS_PLANT", "BRACT",
                                      "**OTHER_PLANT_TISSUE**", "MYCELIUM", "MYCORRHIZA",
                                      "SPORE_BEARING_STRUCTURE", "HOLDFAST_FUNGI", "STIPE",
                                      "CAP", "GILL_FUNGI", "THALLUS_FUNGI", "SPORE",
                                      "**OTHER_FUNGAL_TISSUE**", "NOT_COLLECTED",
                                      "NOT_APPLICABLE", "NOT_PROVIDED", "DNA_EXTRACT",
                                      "MOLLUSC_FOOT", "UNICELLULAR_ORGANISMS_IN_CULTURE",
                                      "MULTICELLULAR_ORGANISMS_IN_CULTURE"]},
                  {"python_name": "barcode_plate_preservative",
                   "field_name": "BARCODE_PLATE_PRESERVATIVE",
                   "required": False},
                  {"python_name": "purpose_of_specimen",
                   "field_name": "PURPOSE_OF_SPECIMEN",
                   "required": False,
                   "allowed_values": ["REFERENCE_GENOME", "SHORT_READ_SEQUENCING",
                                      "DNA_BARCODING_ONLY", "RNA_SEQUENCING", "R&D"]},
                  {"python_name": "hazard_group",
                   "field_name": "HAZARD_GROUP",
                   "required": False,
                   "allowed_values": ["HG1", "HG2", "HG3"]},
                  {"python_name": "regulatory_compliance",
                   "field_name": "REGULATORY_COMPLIANCE",
                   "required": False,
                   "allowed_values": ["Y", "N", "NOT_APPLICABLE"]},
                  {"python_name": "original_collection_date",
                   "field_name": "ORIGINAL_COLLECTION_DATE",  # Validated in ENA checklist
                   "required": False},
                  {"python_name": "original_geographic_location",
                   "field_name": "ORIGINAL_GEOGRAPHIC_LOCATION",
                   "required": False},  # Validated in ENA checklist
                  {"python_name": "barcode_hub",
                   "field_name": "BARCODE_HUB",  # Validated in ENA checklist
                   "required": False}]

    id_fields = [{"python_name": "tolid",
                  "field_name": "tolId",
                  "required": True},
                 {"python_name": "sample_same_as",
                  "field_name": "sampleSameAs",
                  "required": True},
                 {"python_name": "sample_derived_from",
                  "field_name": "sampleDerivedFrom",
                  "required": True},
                 {"python_name": "sample_symbiont_of",
                  "field_name": "sampleSymbiontOf",
                  "required": True},
                 {"python_name": "biosample_accession",
                  "field_name": "biosampleAccession",
                  "required": True},
                 {"python_name": "sra_accession",
                  "field_name": "sraAccession",
                  "required": True},
                 {"python_name": "submission_accession",
                  "field_name": "submissionAccession",
                  "required": True},
                 {"python_name": "submission_error",
                  "field_name": "submissionError",
                  "required": True}]

    specimen_id_patterns = {
        "UNIVERSITY OF OXFORD": [{"prefix": "Ox", "suffix": r'\d{6}'}],
        "MARINE BIOLOGICAL ASSOCIATION": [{"prefix": "MBA", "suffix": r'-\d{5}-\d{3}[A-Z]'}],
        "ROYAL BOTANIC GARDENS KEW": [{"prefix": "KDTOL", "suffix": r'\d{5}'}],
        "ROYAL BOTANIC GARDEN EDINBURGH": [{"prefix": "EDTOL", "suffix": r'\d{5}'}],
        "EARLHAM INSTITUTE": [{"prefix": "EI_", "suffix": r'\d{5}'}],
        "NATURAL HISTORY MUSEUM": [{"prefix": "NHMUK", "suffix": r'\d{9}'}],
        "SANGER INSTITUTE": [{"prefix": "SAN", "suffix": r'\d{7}'},
                             {"prefix": "BLAX", "suffix": r'\d{7}'}],
        "UNIVERSITY OF DERBY": [{"prefix": "UDUK"}],
        "DALHOUSIE UNIVERSITY": [{"prefix": "DU"}],
        "NOVA SOUTHEASTERN UNIVERSITY": [{"prefix": "NSU"}],
        "GEOMAR HELMHOLTZ CENTRE": [{"prefix": "GHC"}],
        "UNIVERSITY OF BRITISH COLUMBIA": [{"prefix": "UOBC"}],
        "UNIVERSITY OF VIENNA (MOLLUSC)": [{"prefix": "VIEM"}],
        "QUEEN MARY UNIVERSITY OF LONDON": [{"prefix": "QMOUL"}],
        "THE SAINSBURY LABORATORY": [{"prefix": "SL"}],
        "PORTLAND STATE UNIVERSITY": [{"prefix": "PORT"}],
        "UNIVERSITY OF RHODE ISLAND": [{"prefix": "URI"}],
        "UNIVERSITY OF CALIFORNIA": [{"prefix": "UCALI"}],
        "SENCKENBERG RESEARCH INSTITUTE": [{"prefix": "SENCK"}],
        "UNIVERSITY OF VIENNA (CEPHALOPOD)": [{"prefix": "VIEC"}],
        "UNIVERSITY OF ORGEON": [{"prefix": "UOREG"}]
    }
