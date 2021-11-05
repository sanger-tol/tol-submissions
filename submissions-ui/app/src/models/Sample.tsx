{/*
SPDX-FileCopyrightText: 2021 Genome Research Ltd.

SPDX-License-Identifier: MIT
*/}

export interface Sample {
    row: number;
    SPECIMEN_ID: string;
    TAXON_ID: number;
    SCIENTIFIC_NAME: string;
    GENUS: string;
    FAMILY: string;
    ORDER_OR_GROUP: string;
    COMMON_NAME: string;
    LIFESTAGE: string;
    SEX: string;
    ORGANISM_PART: string;
    GAL: string;
    GAL_SAMPLE_ID: string;
    COLLECTED_BY: string;
    COLLECTOR_AFFILIATION: string;
    DATE_OF_COLLECTION: string;
    COLLECTION_LOCATION: string;
    DECIMAL_LATITUDE: string;
    DECIMAL_LONGITUDE: string;
    HABITAT: string;
    IDENTIFIED_BY: string;
    IDENTIFIER_AFFILIATION: string;
    VOUCHER_ID: string;
    OTHER_INFORMATION: string;
    ELEVATION: string;
    DEPTH: string;
    RELATIONSHIP: string;
    SYMBIONT: string;
    CULTURE_OR_STRAIN_ID: string;
    SERIES: string;
    RACK_OR_PLATE_ID: string;
    TUBE_OR_WELL_ID: string;
    TAXON_REMARKS: string;
    INFRASPECIFIC_EPITHET: string;
    COLLECTOR_SAMPLE_ID: string;
    GRID_REFERENCE: string;
    TIME_OF_COLLECTION: string;
    DESCRIPTION_OF_COLLECTION_METHOD: string;
    DIFFICULT_OR_HIGH_PRIORITY_SAMPLE: string;
    IDENTIFIED_HOW: string;
    SPECIMEN_ID_RISK: string;
    PRESERVED_BY: string;
    PRESERVER_AFFILIATION: string;
    PRESERVATION_APPROACH: string;
    PRESERVATIVE_SOLUTION: string;
    TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION: string;
    DATE_OF_PRESERVATION: string;
    SIZE_OF_TISSUE_IN_TUBE: string;
    TISSUE_REMOVED_FOR_BARCODING: string;
    PLATE_ID_FOR_BARCODING: string;
    TUBE_OR_WELL_ID_FOR_BARCODING: string;
    TISSUE_FOR_BARCODING: string;
    BARCODE_PLATE_PRESERVATIVE: string;
    PURPOSE_OF_SPECIMEN: string;
    HAZARD_GROUP: string;
    REGULATORY_COMPLIANCE: string;
    ORIGINAL_COLLECTION_DATE: string;
    ORIGINAL_GEOGRAPHIC_LOCATION: string;
    BARCODE_HUB: string;
    tolId: string;
    biosampleAccession: string;
    sraAccession: string;
    submissionAccession: string;
    submissionError: string;
    sampleDerivedFrom: string;
    sampleSameAs: string;
    sampleSymbiontOf: string;
}
