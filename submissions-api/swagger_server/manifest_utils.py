from swagger_server.model import SubmissionsManifest, SubmissionsSample


def create_manifest_from_json(samples):
    manifest = SubmissionsManifest()
    for s in samples:
        sample = SubmissionsSample()
        sample.manifest = manifest
        sample.row = s.get('row')
        sample.specimen_id = s.get('SPECIMEN_ID')
        sample.taxonomy_id = s.get('TAXON_ID')
        sample.scientific_name = s.get('SCIENTIFIC_NAME')
        sample.common_name = s.get('COMMON_NAME')
        sample.lifestage = s.get('LIFESTAGE')
        sample.sex = s.get('SEX')
        sample.organism_part = s.get('ORGANISM_PART')
        sample.GAL = s.get('GAL')
        sample.GAL_sample_id = s.get('GAL_SAMPLE_ID')
        sample.collected_by = s.get('COLLECTED_BY')
        sample.collector_affiliation = s.get('COLLECTOR_AFFILIATION')
        sample.date_of_collection = s.get('DATE_OF_COLLECTION')
        sample.collection_location = s.get('COLLECTION_LOCATION')
        sample.decimal_latitude = s.get('DECIMAL_LATITUDE')
        sample.decimal_longitude = s.get('DECIMAL_LONGITUDE')
        sample.habitat = s.get('HABITAT')
        sample.identified_by = s.get('IDENTIFIED_BY')
        sample.identifier_affiliation = s.get('IDENTIFIER_AFFILIATION')
        sample.voucher_id = s.get('VOUCHER_ID')
        sample.elevation = s.get('ELEVATION')
        sample.depth = s.get('DEPTH')
        sample.relationship = s.get('RELATIONSHIP')
        # The following are not added here
        # biosampleId
        # tolId
    return manifest


def validate_manifest(manifest):
    results = []
    number_of_errors = 0
    for sample in manifest.samples:
        sample_results = validate_sample(sample)
        results.append({'row': sample.row,
                        'results': sample_results})
        number_of_errors += len(sample_results)
    return number_of_errors, results


def validate_sample(sample):
    results = []

    if sample.scientific_name == "":
        results.append({'field': 'SCIENTIFIC_NAME',
                        'message': 'Scientific name must be given'})

    return results
