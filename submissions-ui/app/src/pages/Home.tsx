import React from "react";
import { Link } from "react-router-dom";

function Home() {
  return (
    <div className="home">
      <header className="masthead text-center text-white">
        <div className="masthead-content">
          <div className="container">
            <h1 className="masthead-heading mb-0">ToL Submissions</h1>
            <h2 className="masthead-subheading mb-0">Tree of Life Submissions</h2>
            <a href="api/v1/ui/" className="btn btn-primary btn-xl rounded-pill mt-5">Use the API</a>
          </div>
        </div>
        <div className="bg-circle-1 bg-circle"></div>
        <div className="bg-circle-2 bg-circle"></div>
        <div className="bg-circle-3 bg-circle"></div>
        <div className="bg-circle-4 bg-circle"></div>
      </header>

      <section>
        <div className="container">
          <div className="row align-items-center">
            <div className="col-lg-12 order-lg-1">
              <div className="p-5">
                <h2 className="display-4">What are submissions?</h2>
                <p>Submissions is a Sanger internal service for generating ENA and Biosample IDs from sample manifests.
                  It is called from STS but can also be used on its own. It's developed and maintained by the
                  <a href="mailto:tol-platforms@sanger.ac.uk">Tree of Life Enabling Platforms team</a>.
                </p>
                <h2 className="display-4">How can I use it?</h2>
                <p>At the moment, all use is via the API. To start using the API you'll need to ask us for an API key.
                  Once you have this you can call all the API endpoints.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Home;