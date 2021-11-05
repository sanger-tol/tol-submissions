{/*
SPDX-FileCopyrightText: 2021 Genome Research Ltd.

SPDX-License-Identifier: MIT
*/}

import React from "react";
import { Container, Row, Col } from "react-bootstrap"; 
import { Link } from "react-router-dom";

function Home() {
  return (
    <div className="home">
      <header className="masthead text-center text-white">
        <div className="masthead-content">
          <Container>
            <h1 className="masthead-heading mb-0">ToL Submissions</h1>
            <h2 className="masthead-subheading mb-0">Tree of Life Submissions</h2>
            <a href="api/v1/ui/" className="btn btn-primary btn-xl rounded-pill mt-5">Use the API</a>
            <Link to="/search" className="btn btn-primary btn-xl rounded-pill mt-5">Search</Link>
          </Container>
        </div>
        <div className="bg-circle-1 bg-circle"></div>
        <div className="bg-circle-2 bg-circle"></div>
        <div className="bg-circle-3 bg-circle"></div>
        <div className="bg-circle-4 bg-circle"></div>
      </header>

      <section>
        <Container>
          <Row className="align-items-center">
            <Col lg="12" className="order-lg-1">
              <div className="p-5">
                <h2 className="display-4">What are submissions?</h2>
                <p>Submissions is a Sanger internal service for validating sample manifests and generating ENA and BioSamples
                  accessions from them. It is called from STS but can also be used on its own. It's developed and maintained by the
                  <a href="mailto:tol-platforms@sanger.ac.uk"> Tree of Life Enabling Platforms team</a>.
                </p>
                <h2 className="display-4">How can I use it?</h2>
                <p>At the moment, all use is via the API. To start using the API you'll need to ask us for an API key.
                  Once you have this you can call all the API endpoints.
                </p>
                <h3>Starting with an Excel manifest</h3>
                <ul>
                  <li>Use the <code>manifests/upload-excel</code> endpoint to upload the manifest. This returns the manifest ID as part of the returned JSON.</li>
                  <li>Use the <code>manifests/{'{'}manifestId{'}'}/validate</code> endpoint to validate the manifest contents. This will return a list of errors and warnings.</li>
                  <li>If validation is successful, the <code>manifests/{'{'}manifestId{'}'}/generate</code> endpoint will generate and return the ENA and BioSamples accessions.</li>
                  <li>If validation is not successful, correct the errors in the Excel manifest and re-upload, noting that this will result in a new manifest ID.</li>
                </ul>
                <h3>Starting with a JSON manifest</h3>
                <ul>
                  <li>Use the <code>manifests</code> POST endpoint to upload the manifest. This returns the manifest ID as part of the returned JSON.</li>
                  <li>Use the <code>manifests/{'{'}manifestId{'}'}/validate</code> endpoint to validate the manifest contents. This will return a list of errors and warnings.</li>
                  <li>If validation is successful, the <code>manifests/{'{'}manifestId{'}'}/generate</code> endpoint will generate and return the ENA and BioSamples accessions.</li>
                  <li>If validation is not successful, correct the errors in the JSON manifest and re-upload, noting that this will result in a new manifest ID.</li>
                </ul>
              </div>
            </Col>
          </Row>
        </Container>
      </section>
    </div>
  );
}

export default Home;