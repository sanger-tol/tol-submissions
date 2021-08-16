import React from 'react';
import { Specimen } from '../../models/Specimen';
import { Table } from 'react-bootstrap';
import { StyledSearchResultsSpecimen } from './SearchResultsSpecimenStyled'
import SearchResultsSpecimenSampleList from './SearchResultsSpecimenSampleList';

interface SearchResultsSpecimenProps {
    specimen: Specimen;
}

const SearchResultsSample: React.FunctionComponent<SearchResultsSpecimenProps> = ({
    specimen,
}: SearchResultsSpecimenProps) => {

    return (
        <StyledSearchResultsSpecimen className="specimen-search-result">
            <span className="search-result-main-heading">Specimen found.</span><br/>
            <Table>
                <tbody>
                    <tr>
                        <td>Specimen ID</td>
                        <td>{specimen.specimenId}</td>
                    </tr>
                    <tr>
                        <td>Biospecimen ID</td>
                        <td>{specimen.biospecimenId}</td>
                    </tr>
                </tbody>
            </Table>
            <hr></hr>
            <SearchResultsSpecimenSampleList samples={specimen.samples}/>
        </StyledSearchResultsSpecimen>
    );
};

export default SearchResultsSample;