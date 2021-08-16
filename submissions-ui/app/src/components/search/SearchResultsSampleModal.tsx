import { Sample } from '../../models/Sample';
import { Button, Table, Modal } from 'react-bootstrap';
import { StyledSearchResultsSampleModal } from './SearchResultsSampleModalStyled';
import { MouseEvent } from 'react';

interface SearchResultsSampleModalProps {
    sample: Sample;
    onClose: (event: MouseEvent) => void;
}

const SearchResultsSampleModal: React.FunctionComponent<SearchResultsSampleModalProps> = ({
    sample,
    onClose
}: SearchResultsSampleModalProps) => {
    return (
        <StyledSearchResultsSampleModal>
            <Modal.Title>Sample Details</Modal.Title>
            <Table striped={true}>
                <tbody>
                    <tr>
                        <td>Biosample ID</td>
                        <td>{sample.biosampleAccession || '-' }</td>
                    </tr>
                    <tr>
                        <td>Rack or Plate ID</td>
                        <td>{sample.RACK_OR_PLATE_ID || '-' }</td>
                    </tr>
                    <tr>
                        <td>Tube or Well ID</td>
                        <td>{sample.TUBE_OR_WELL_ID || '-' }</td>
                    </tr>
                    <tr>
                        <td>Taxonomy ID</td>
                        <td>{sample.TAXON_ID || '-' }</td>
                    </tr>
                    <tr>
                        <td>Scientific Name</td>
                        <td>{sample.SCIENTIFIC_NAME || '-' }</td>
                    </tr>
                    <tr>
                        <td>Genus</td>
                        <td>{sample.GENUS || '-' }</td>
                    </tr>
                    <tr>
                        <td>Family</td>
                        <td>{sample.FAMILY || '-' }</td>
                    </tr>
                    <tr>
                        <td>Order or Group</td>
                        <td>{sample.ORDER_OR_GROUP || '-' }</td>
                    </tr>
                    <tr>
                        <td>Common Name</td>
                        <td>{sample.COMMON_NAME || '-' }</td>
                    </tr>
                    <tr>
                        <td>Lifestage</td>
                        <td>{sample.LIFESTAGE || '-' }</td>
                    </tr>
                    <tr>
                        <td>Sex</td>
                        <td>{sample.SEX || '-' }</td>
                    </tr>
                    <tr>
                        <td>Organism Part</td>
                        <td>{sample.ORGANISM_PART || '-' }</td>
                    </tr>
                    <tr>
                        <td>GAL</td>
                        <td>{sample.GAL || '-' }</td>
                    </tr>
                    <tr>
                        <td>Collected by</td>
                        <td>{sample.COLLECTED_BY || '-' }</td>
                    </tr>
                    <tr>
                        <td>Collector Affiliation</td>
                        <td>{sample.COLLECTOR_AFFILIATION || '-' }</td>
                    </tr>
                    <tr>
                        <td>Date of Collection</td>
                        <td>{sample.DATE_OF_COLLECTION || '-' }</td>
                    </tr>
                    <tr>
                        <td>Collection Location</td>
                        <td>{sample.COLLECTION_LOCATION || '-' }</td>
                    </tr>
                    <tr>
                        <td>Decimal Latitude</td>
                        <td>{sample.DECIMAL_LATITUDE || '-' }</td>
                    </tr>
                    <tr>
                        <td>Decimal Longitude</td>
                        <td>{sample.DECIMAL_LONGITUDE || '-' }</td>
                    </tr>
                    <tr>
                        <td>Habitat</td>
                        <td>{sample.HABITAT || '-' }</td>
                    </tr>
                    <tr>
                        <td>Identified by</td>
                        <td>{sample.IDENTIFIED_BY || '-' }</td>
                    </tr>
                    <tr>
                        <td>Identifier Affiliation</td>
                        <td>{sample.IDENTIFIER_AFFILIATION || '-' }</td>
                    </tr>
                    <tr>
                        <td>Voucher ID</td>
                        <td>{sample.VOUCHER_ID || '-' }</td>
                    </tr>
                    <tr>
                        <td>Other Information</td>
                        <td>{sample.OTHER_INFORMATION || '-' }</td>
                    </tr>
                    <tr>
                        <td>Elevation</td>
                        <td>{sample.ELEVATION || '-' }</td>
                    </tr>
                    <tr>
                        <td>Depth</td>
                        <td>{sample.DEPTH || '-' }</td>
                    </tr>
                    <tr>
                        <td>Relationship</td>
                        <td>{sample.RELATIONSHIP || '-' }</td>
                    </tr>
                    <tr>
                        <td>Symbiont</td>
                        <td>{sample.SYMBIONT || '-' }</td>
                    </tr>
                    <tr>
                        <td>Culture or Strain ID</td>
                        <td>{sample.CULTURE_OR_STRAIN_ID || '-' }</td>
                    </tr>
                    <tr>
                        <td>Series</td>
                        <td>{sample.SERIES || '-' }</td>
                    </tr>
                    <tr>
                        <td>Taxonomy Remarks</td>
                        <td>{sample.TAXON_REMARKS || '-' }</td>
                    </tr>
                    <tr>
                        <td>Infraspecific Epithet</td>
                        <td>{sample.INFRASPECIFIC_EPITHET || '-' }</td>
                    </tr>
                    <tr>
                        <td>Collector Sample ID</td>
                        <td>{sample.COLLECTOR_SAMPLE_ID || '-' }</td>
                    </tr>
                    <tr>
                        <td>Grid Reference</td>
                        <td>{sample.GRID_REFERENCE || '-' }</td>
                    </tr>
                    <tr>
                        <td>Time of Collection</td>
                        <td>{sample.TIME_OF_COLLECTION || '-' }</td>
                    </tr>
                    <tr>
                        <td>Description of Collection Method</td>
                        <td>{sample.DESCRIPTION_OF_COLLECTION_METHOD || '-' }</td>
                    </tr>
                    <tr>
                        <td>Difficult or High Priority Sample</td>
                        <td>{sample.DIFFICULT_OR_HIGH_PRIORITY_SAMPLE || '-' }</td>
                    </tr>
                    <tr>
                        <td>Identified how</td>
                        <td>{sample.IDENTIFIED_HOW || '-' }</td>
                    </tr>
                    <tr>
                        <td>Specimen ID Risk</td>
                        <td>{sample.SPECIMEN_ID_RISK || '-' }</td>
                    </tr>
                    <tr>
                        <td>Preserved by</td>
                        <td>{sample.PRESERVED_BY || '-' }</td>
                    </tr>
                    <tr>
                        <td>Preserver Affiliation</td>
                        <td>{sample.PRESERVER_AFFILIATION || '-' }</td>
                    </tr>
                    <tr>
                        <td>Preservation Approach</td>
                        <td>{sample.PRESERVATION_APPROACH || '-' }</td>
                    </tr>
                    <tr>
                        <td>Preservation Solution</td>
                        <td>{sample.PRESERVATIVE_SOLUTION || '-' }</td>
                    </tr>
                    <tr>
                        <td>Time Elapsed from Collection to Preservation</td>
                        <td>{sample.TIME_ELAPSED_FROM_COLLECTION_TO_PRESERVATION || '-' }</td>
                    </tr>
                    <tr>
                        <td>Date of Preservation</td>
                        <td>{sample.DATE_OF_PRESERVATION || '-' }</td>
                    </tr>
                    <tr>
                        <td>Size of Tissue in Tube</td>
                        <td>{sample.SIZE_OF_TISSUE_IN_TUBE || '-' }</td>
                    </tr>
                    <tr>
                        <td>Tissue Removed for Barcoding</td>
                        <td>{sample.TISSUE_REMOVED_FOR_BARCODING || '-' }</td>
                    </tr>
                    <tr>
                        <td>Plate ID for Barcoding</td>
                        <td>{sample.PLATE_ID_FOR_BARCODING || '-' }</td>
                    </tr>
                    <tr>
                        <td>Tube or Well ID for Barcoding</td>
                        <td>{sample.TUBE_OR_WELL_ID_FOR_BARCODING || '-' }</td>
                    </tr>
                    <tr>
                        <td>Tissue for Barcoding</td>
                        <td>{sample.TISSUE_FOR_BARCODING || '-' }</td>
                    </tr>
                    <tr>
                        <td>Barcode Plate Preservative</td>
                        <td>{sample.BARCODE_PLATE_PRESERVATIVE || '-' }</td>
                    </tr>
                    <tr>
                        <td>Purpose of Specimen</td>
                        <td>{sample.PURPOSE_OF_SPECIMEN || '-' }</td>
                    </tr>
                    <tr>
                        <td>Hazard Group</td>
                        <td>{sample.HAZARD_GROUP || '-' }</td>
                    </tr>
                    <tr>
                        <td>Regulatory Compliance</td>
                        <td>{sample.REGULATORY_COMPLIANCE || '-' }</td>
                    </tr>
                    <tr>
                        <td>Original Collection Date</td>
                        <td>{sample.ORIGINAL_COLLECTION_DATE || '-' }</td>
                    </tr>
                    <tr>
                        <td>Original Geographic Location</td>
                        <td>{sample.ORIGINAL_GEOGRAPHIC_LOCATION || '-' }</td>
                    </tr>
                    <tr>
                        <td>Barcode HUB</td>
                        <td>{sample.BARCODE_HUB || '-' }</td>
                    </tr>
                    <tr>
                        <td>Tree of Life ID</td>
                        <td>{sample.tolId || '-' }</td>
                    </tr>
                    <tr>
                        <td>SRA Accession</td>
                        <td>{sample.sraAccession || '-' }</td>
                    </tr>
                    <tr>
                        <td>Submission Error</td>
                        <td>{sample.submissionError || '-' }</td>
                    </tr>
                    <tr>
                        <td>Sample Derived From</td>
                        <td>{sample.sampleDerivedFrom || '-' }</td>
                    </tr>
                    <tr>
                        <td>Sample Same as</td>
                        <td>{sample.sampleSameAs || '-' }</td>
                    </tr>
                    <tr>
                        <td>Sample Symbiont of</td>
                        <td>{sample.sampleSymbiontOf || '-' }</td>
                    </tr>
                </tbody>
            </Table>
            <Button variant="primary" onClick={onClose}>Close Sample</Button>
        </StyledSearchResultsSampleModal>
    );
}

export default SearchResultsSampleModal;
