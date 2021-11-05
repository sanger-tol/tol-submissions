{/*
SPDX-FileCopyrightText: 2021 Genome Research Ltd.

SPDX-License-Identifier: MIT
*/}

import * as React from 'react';
import { Sample } from '../../models/Sample'
import { Specimen } from '../../models/Specimen'
import SearchResultsSample from './SearchResultsSample';
import SearchResultsSpecimen from './SearchResultsSpecimen'
import './SearchResults.scss'

export interface Props {
    list?: string[]
}
export interface State {
    alreadySearched: boolean;
    specimen: Specimen | null;
    sample: Sample | null;
}

function getSample(searchTerm: string): Promise<Sample> {
    return fetch('/api/v1/samples/'+searchTerm)
        // the JSON body is taken from the response
        .then(res => {
            if (res.ok) { 
             return res.json();
            }
            return null; 
          })
        .then(res => {
            return res as Sample;
        })
}

function getSpecimenBySpecimenId(searchTerm: string): Promise<Specimen> {
    return fetch('/api/v1/specimens/specimenId/'+searchTerm+'/samples')
        // the JSON body is taken from the response
        .then(res => {
            if (res.ok) { 
              return res.json();
            }
            return null; 
          })
        .then(res => {
            return res as Specimen
        })
}

function getBiospecimenBySpecimenId(searchTerm: string): Promise<Specimen> {
  return fetch('/api/v1/specimens/biospecimenId/'+searchTerm+'/samples')
      // the JSON body is taken from the response
      .then(res => {
          if (res.ok) { 
            return res.json();
          }
          return null; 
        })
      .then(res => {
          return res as Specimen
      })
}

class SearchResults extends React.Component<Props, State> {
    constructor(props: Props) {
      super(props);
      this.state = {
        alreadySearched: false,
        sample: null,
        specimen: null
      }
    }

    doSearch = (event: any) => {
        event.preventDefault();
        const searchTerm = document.getElementById("searchInput") as HTMLInputElement;
        const form = document.getElementById("searchForm") as HTMLFormElement;
        // If our input has a value
        if (searchTerm.value !== "") {
          getSample(searchTerm.value)
            .then(sample => this.setState({ sample: sample }));
            getSpecimenBySpecimenId(searchTerm.value)
            .then(specimen => this.setState({ specimen: specimen }));
            getBiospecimenBySpecimenId(searchTerm.value)
            .then(specimen => this.setState({ specimen: specimen }))
          this.setState({ alreadySearched: true })
          // Finally, we need to reset the form
          searchTerm.classList.remove("is-invalid");
          form.reset();
        } else {
          // If the input doesn't have a value, make the border red since it's required
          searchTerm.classList.add("is-invalid");
        }
    };

    public render() {
      return (
        <div>
            <form className="form" id="searchForm">
                <div className="form-group">
                    <input type="text" className="form-control form-control-lg" id="searchInput" placeholder="Search..." />
                    <small className="form-text text-muted">
                        Search on Biosample ID (for samples), or Specimen ID or Biospecimen ID (for specimens)
                    </small>
                </div>
                <button className="btn btn-primary" id="searchButton" onClick={this.doSearch}>
                Search
                </button>
            </form>
            <div className="searchResults col-6">
              {this.state.alreadySearched && this.state.sample !== null &&
                <div className="sample-search-result">
                  <span className="search-result-main-heading">Sample Found</span><br/>
                  <SearchResultsSample sample={this.state.sample}/>
                </div>
              }
              {this.state.alreadySearched && this.state.specimen !== null &&
                <div>
                  <SearchResultsSpecimen specimen={this.state.specimen}/>
                </div>
              }
                
            </div>
            {this.state.sample === null && this.state.specimen === null && this.state.alreadySearched &&
            <p>
                No results found
            </p>
            }
        </div>
      );
    }
  }
  export default SearchResults;