/*
SPDX-FileCopyrightText: 2021 Genome Research Ltd.

SPDX-License-Identifier: MIT
*/

import { Sample } from '../../models/Sample';
import { StyledSearchResultsSpecimenSampleList } from './SearchResultsSpecimenSampleListStyled';
import SearchResultsSample from './SearchResultsSample';

interface SearchResultsSpecimenSampleProps {
    samples: Sample[];
}

const SearchResultsSpecimenSampleList: React.FunctionComponent<SearchResultsSpecimenSampleProps> = ({
    samples,
}: SearchResultsSpecimenSampleProps) => {
    if (samples.length === 0) {
        return (
            <StyledSearchResultsSpecimenSampleList>
                <span className="search-result-heading">No samples found for this specimen.</span><br/>
            </StyledSearchResultsSpecimenSampleList>
        )
    }

    return (
        <StyledSearchResultsSpecimenSampleList>
            <span className="search-result-heading">With the following samples:</span><br/>
            <ul className="specimen-sample-list">
                {samples.map((item: Sample) =>
                    <li className="specimen-sample" key={item.biosampleAccession}><SearchResultsSample sample={item}/></li>
                )
                }
            </ul>            
        </StyledSearchResultsSpecimenSampleList>
    );
};

export default SearchResultsSpecimenSampleList;
