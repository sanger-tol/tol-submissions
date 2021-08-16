import React from 'react';
import { render, screen } from '@testing-library/react';
import Search from './Search';
import userEvent from '@testing-library/user-event';
import { act } from "react-dom/test-utils";

afterEach(() => {
    // remove the mock to ensure tests are completely isolated
    if (global.fetch.mock) {
        global.fetch.mockRestore();
    }
});

test('renders search page link', () => {
    render(<Search />);
    expect(screen.queryAllByText("Search")).not.toHaveLength(0);
});

// helper function for ok'ing only matching API requests
const mockFetchOnMatch = (regex: string, obj: object) => {
    jest.spyOn(global, "fetch").mockImplementation((
        input: RequestInfo,
        init?: RequestInit | undefined
    ) => {
        const compiledRegex = RegExp(regex);
        const match = compiledRegex.test(input as string);
        const body = match ? obj : null;

        return Promise.resolve({
            json: () => Promise.resolve(body),
            ok: match
        });
    });
}

const doSearch = async () => {
    const input = screen.queryByRole('textbox');
    userEvent.type(input, "doesn't matter");
    const searchButton = screen.queryByRole('button');
    userEvent.click(searchButton);
}

const openModal = async () => {
    // this is a fragile query, if anything moves, or another
    // button is added, it will break
    const openModalButton = screen.queryAllByRole('button')[1];
    userEvent.click(openModalButton);
}

const testModal = fakeSample => {
    const excludedKeys = [
        "row",
        "SPECIMEN_ID",
        "GAL_SAMPLE_ID",
        "submissionAccession"
    ];
    Object.keys(fakeSample)
        .filter(key => !excludedKeys.includes(key))
        .forEach((key, index) => {
            expect(screen.queryAllByText(fakeSample[key])).not.toHaveLength(0);
        });
}

test('renders a fake specimen retrieved by its specimen ID', async () => {
    const fakeSpecimen = {
        "specimenId": "FAKE_SPECIMEN_ID",
        "biospecimenId": "FAKE_BIOSPECIMEN_ID",
        "samples": [],
    };
    
    mockFetchOnMatch("^/api/v1/specimens/specimenId/", fakeSpecimen);

    render(<Search />);
    await act(doSearch);

    expect(screen.queryAllByText(fakeSpecimen.specimenId)).not.toHaveLength(0);
    expect(screen.queryAllByText(fakeSpecimen.biospecimenId)).not.toHaveLength(0);

});

test('renders a fake specimen retrieved by its biospecimen ID', async () => {
    const fakeSpecimen = {
        "specimenId": "ANOTHER_FAKE_SPECIMEN_ID",
        "biospecimenId": "ANOTHER_FAKE_BIOSPECIMEN_ID",
        "samples": [],
    };
    
    mockFetchOnMatch("^/api/v1/specimens/biospecimenId/", fakeSpecimen);

    render(<Search />);
    await act(doSearch);

    expect(screen.queryAllByText(fakeSpecimen.specimenId)).not.toHaveLength(0);
    expect(screen.queryAllByText(fakeSpecimen.biospecimenId)).not.toHaveLength(0);
});

test('renders a fake sample retrieved by its biosample ID', async () => {
    const fakeSample = {
        "row": 0,
        "SPECIMEN_ID": "A_SPECIMEN_ID",
        "TAXON_ID": 67890,
        "SCIENTIFIC_NAME": "A_SCIENTIFIC_NAME",
        "GENUS": "A_GENUS",
        "FAMILY": "A_FAMILY",
        "ORDER_OR_GROUP": "AN_ORDER_OR_GROUP",
        "COMMON_NAME": "A_COMMON_NAME",
        "LIFESTAGE": "A_LIFESTAGE",
        "SEX": "A_SEX",
        "ORGANISM_PART": "AN_ORGANISM_PART",
        "GAL": "A_GAL",
        "GAL_SAMPLE_ID": "A_GAL_SAMPLE_ID",
        "COLLECTED_BY": "COLLECTED_BY",
        "COLLECTOR_AFFILIATION": "COLLECTOR_AFFILIATION",
        "DATE_OF_COLLECTION": "DATE_OF_COLLECTION",
        "COLLECTION_LOCATION": "COLLECTION_LOCATION",
        "DECIMAL_LATITUDE": "DECIMAL_LATITUDE",
        "DECIMAL_LONGITUDE": "DECIMAL_LONGITUDE",
        "HABITAT": "HABITAT",
        "IDENTIFIED_BY": "IDENTIFIED_BY",
        "IDENTIFIER_AFFILIATION": "IDENTIFIER_AFFILIATION",
        "VOUCHER_ID": "VOUCHER_ID",
        "OTHER_INFORMATION": "OTHER_INFORMATION",
        "ELEVATION": "ELEVATION",
        "DEPTH": "DEPTH",
        "RELATIONSHIP": "RELATIONSHIP",
        "SYMBIONT": "SYMBIONT",
        "CULTURE_OR_STRAIN_ID": "CULTURE_OR_STRAIN_ID",
        "SERIES": "SERIES",
        "RACK_OR_PLATE_ID": "RACK_OR_PLATE_ID",
        "TUBE_OR_WELL_ID": "TUBE_OR_WELL_ID",
        "TAXON_REMARKS": "TAXON_REMARKS",
        "INFRASPECIFIC_EPITHET": "INFRASPECIFIC_EPITHET",
        "COLLECTOR_SAMPLE_ID": "COLLECTOR_SAMPLE_ID",
        "GRID_REFERENCE": "GRID_REFERENCE",
        "TIME_OF_COLLECTION": "TIME_OF_COLLECTION",
        "DESCRIPTION_OF_COLLECTION_METHOD": "DESCRIPTION_OF_COLLECTION_METHOD",
        "DIFFICULT_OR_HIGH_PRIORITY_SAMPLE": "DIFFICULT_OR_HIGH_PRIORITY_SAMPLE",
        "IDENTIFIED_HOW": "IDENTIFIED_HOW",
        "SPECIMEN_ID_RISK": "SPECIMEN_ID_RISK",
        "PRESERVED_BY": "PRESERVED_BY",
        "PRESERVER_AFFILIATION": "PRESERVER_AFFILIATION",
        "PRESERVATION_APPROACH": "PRESERVATION_APPROACH",
        "PRESERVATIVE_SOLUTION": "PRESERVATIVE_SOLUTION",
        "TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION": "TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION",
        "DATE_OF_PRESERVATION": "DATE_OF_PRESERVATION",
        "SIZE_OF_TISSUE_IN_TUBE": "SIZE_OF_TISSUE_IN_TUBE",
        "TISSUE_REMOVED_FOR_BARCODING": "TISSUE_REMOVED_FOR_BARCODING",
        "PLATE_ID_FOR_BARCODING": "PLATE_ID_FOR_BARCODING",
        "TUBE_OR_WELL_ID_FOR_BARCODING": "TUBE_OR_WELL_ID_FOR_BARCODING",
        "TISSUE_FOR_BARCODING": "TISSUE_FOR_BARCODING",
        "BARCODE_PLATE_PRESERVATIVE": "BARCODE_PLATE_PRESERVATIVE",
        "PURPOSE_OF_SPECIMEN": "PURPOSE_OF_SPECIMEN",
        "HAZARD_GROUP": "HAZARD_GROUP",
        "REGULATORY_COMPLIANCE": "REGULATORY_COMPLIANCE",
        "ORIGINAL_COLLECTION_DATE": "ORIGINAL_COLLECTION_DATE",
        "ORIGINAL_GEOGRAPHIC_LOCATION": "ORIGINAL_GEOGRAPHIC_LOCATION",
        "BARCODE_HUB": "BARCODE_HUB",
        "tolId": "tolId",
        "biosampleAccession": "a_biosampleAccession",
        "sraAccession": "an_sraAccession",
        "submissionAccession": "submissionAccession",
        "submissionError": "submissionError",
        "sampleDerivedFrom": "sampleDerivedFrom",
        "sampleSameAs": "sampleSameAs",
        "sampleSymbiontOf": "sampleSymbiontOf"
    };

    mockFetchOnMatch("^/api/v1/samples/", fakeSample);

    render(<Search />);
    await act(doSearch);

    expect(screen.queryAllByText(fakeSample.biosampleAccession)).not.toHaveLength(0);
    expect(screen.queryAllByText(fakeSample.TUBE_OR_WELL_ID)).not.toHaveLength(0);
    expect(screen.queryAllByText(fakeSample.RACK_OR_PLATE_ID)).not.toHaveLength(0);

    await act(openModal);
    testModal(fakeSample);
});

test('renders a fake specimen with a sample', async () => {
    const fakeSample = {
        "row": 0,
        "SPECIMEN_ID": "A_SPECIMEN_ID",
        "TAXON_ID": 67890,
        "SCIENTIFIC_NAME": "A_SCIENTIFIC_NAME",
        "GENUS": "A_GENUS",
        "FAMILY": "A_FAMILY",
        "ORDER_OR_GROUP": "AN_ORDER_OR_GROUP",
        "COMMON_NAME": "A_COMMON_NAME",
        "LIFESTAGE": "A_LIFESTAGE",
        "SEX": "A_SEX",
        "ORGANISM_PART": "AN_ORGANISM_PART",
        "GAL": "A_GAL",
        "GAL_SAMPLE_ID": "A_GAL_SAMPLE_ID",
        "COLLECTED_BY": "COLLECTED_BY",
        "COLLECTOR_AFFILIATION": "COLLECTOR_AFFILIATION",
        "DATE_OF_COLLECTION": "DATE_OF_COLLECTION",
        "COLLECTION_LOCATION": "COLLECTION_LOCATION",
        "DECIMAL_LATITUDE": "DECIMAL_LATITUDE",
        "DECIMAL_LONGITUDE": "DECIMAL_LONGITUDE",
        "HABITAT": "HABITAT",
        "IDENTIFIED_BY": "IDENTIFIED_BY",
        "IDENTIFIER_AFFILIATION": "IDENTIFIER_AFFILIATION",
        "VOUCHER_ID": "VOUCHER_ID",
        "OTHER_INFORMATION": "OTHER_INFORMATION",
        "ELEVATION": "ELEVATION",
        "DEPTH": "DEPTH",
        "RELATIONSHIP": "RELATIONSHIP",
        "SYMBIONT": "SYMBIONT",
        "CULTURE_OR_STRAIN_ID": "CULTURE_OR_STRAIN_ID",
        "SERIES": "SERIES",
        "RACK_OR_PLATE_ID": "RACK_OR_PLATE_ID",
        "TUBE_OR_WELL_ID": "TUBE_OR_WELL_ID",
        "TAXON_REMARKS": "TAXON_REMARKS",
        "INFRASPECIFIC_EPITHET": "INFRASPECIFIC_EPITHET",
        "COLLECTOR_SAMPLE_ID": "COLLECTOR_SAMPLE_ID",
        "GRID_REFERENCE": "GRID_REFERENCE",
        "TIME_OF_COLLECTION": "TIME_OF_COLLECTION",
        "DESCRIPTION_OF_COLLECTION_METHOD": "DESCRIPTION_OF_COLLECTION_METHOD",
        "DIFFICULT_OR_HIGH_PRIORITY_SAMPLE": "DIFFICULT_OR_HIGH_PRIORITY_SAMPLE",
        "IDENTIFIED_HOW": "IDENTIFIED_HOW",
        "SPECIMEN_ID_RISK": "SPECIMEN_ID_RISK",
        "PRESERVED_BY": "PRESERVED_BY",
        "PRESERVER_AFFILIATION": "PRESERVER_AFFILIATION",
        "PRESERVATION_APPROACH": "PRESERVATION_APPROACH",
        "PRESERVATIVE_SOLUTION": "PRESERVATIVE_SOLUTION",
        "TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION": "TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION",
        "DATE_OF_PRESERVATION": "DATE_OF_PRESERVATION",
        "SIZE_OF_TISSUE_IN_TUBE": "SIZE_OF_TISSUE_IN_TUBE",
        "TISSUE_REMOVED_FOR_BARCODING": "TISSUE_REMOVED_FOR_BARCODING",
        "PLATE_ID_FOR_BARCODING": "PLATE_ID_FOR_BARCODING",
        "TUBE_OR_WELL_ID_FOR_BARCODING": "TUBE_OR_WELL_ID_FOR_BARCODING",
        "TISSUE_FOR_BARCODING": "TISSUE_FOR_BARCODING",
        "BARCODE_PLATE_PRESERVATIVE": "BARCODE_PLATE_PRESERVATIVE",
        "PURPOSE_OF_SPECIMEN": "PURPOSE_OF_SPECIMEN",
        "HAZARD_GROUP": "HAZARD_GROUP",
        "REGULATORY_COMPLIANCE": "REGULATORY_COMPLIANCE",
        "ORIGINAL_COLLECTION_DATE": "ORIGINAL_COLLECTION_DATE",
        "ORIGINAL_GEOGRAPHIC_LOCATION": "ORIGINAL_GEOGRAPHIC_LOCATION",
        "BARCODE_HUB": "BARCODE_HUB",
        "tolId": "tolId",
        "biosampleAccession": "a_biosampleAccession",
        "sraAccession": "an_sraAccession",
        "submissionAccession": "submissionAccession",
        "submissionError": "submissionError",
        "sampleDerivedFrom": "sampleDerivedFrom",
        "sampleSameAs": "sampleSameAs",
        "sampleSymbiontOf": "sampleSymbiontOf"
    };
    const fakeSpecimen = {
        "specimenId": "ANOTHER_FAKE_SPECIMEN_ID",
        "biospecimenId": "ANOTHER_FAKE_BIOSPECIMEN_ID",
        "samples": [
            fakeSample
        ],
    };
    
    mockFetchOnMatch("^/api/v1/specimens/biospecimenId/", fakeSpecimen);

    render(<Search />);
    await act(doSearch);

    expect(screen.queryAllByText(fakeSpecimen.specimenId)).not.toHaveLength(0);
    expect(screen.queryAllByText(fakeSpecimen.biospecimenId)).not.toHaveLength(0);

    await act(openModal);
    testModal(fakeSample);
});
