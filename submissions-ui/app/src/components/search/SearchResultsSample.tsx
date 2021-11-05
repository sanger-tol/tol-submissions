{/*
SPDX-FileCopyrightText: 2021 Genome Research Ltd.

SPDX-License-Identifier: MIT
*/}

import { Sample } from '../../models/Sample';
import { StyledSearchResultsSample } from './SearchResultsSampleStyled'
import SearchResultsSampleModal from './SearchResultsSampleModal';
import React, { useState } from 'react';
import { Button, Modal, Table } from 'react-bootstrap'; 

interface SearchResultsSampleProps {
    sample: Sample;
}

const SearchResultsSample: React.FunctionComponent<SearchResultsSampleProps> = ({
    sample,
}: SearchResultsSampleProps) => {
    const [modalOpen, setModalOpen] = useState(false);

    const closeModal = () => {
        setModalOpen(false);
    }

    const openModal = () => {
        setModalOpen(true);
    }

    return (
        <StyledSearchResultsSample>
            <Table>
                <tbody>
                    <tr>
                        <td>Biosample ID</td>
                        <td>{sample.biosampleAccession}</td>
                    </tr>
                    <tr>
                        <td>Rack or Plate ID</td>
                        <td>{sample.RACK_OR_PLATE_ID || '-'}</td>
                    </tr>
                    <tr>
                        <td>Tube or Well ID</td>
                        <td>{sample.TUBE_OR_WELL_ID || '-'}</td>
                    </tr>
                </tbody>
            </Table>
            <Button variant="primary" onClick={openModal}>Open Sample</Button>
            <Modal show={modalOpen} onHide={closeModal}>
                <Modal.Header closeButton>
                    <SearchResultsSampleModal
                        sample={sample}
                        onClose={closeModal}/>
                </Modal.Header>
            </Modal>
        </StyledSearchResultsSample>
    );
};

export default SearchResultsSample;
