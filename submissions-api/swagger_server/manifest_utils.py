def validate_manifest(manifest):
    results = []
    has_validated = True
    for sample in manifest.samples:
        sample_results = validate_sample(sample)
        results.append({'row': sample.row,
                        'results': sample_results})
        has_validated = has_validated and (len(sample_results) == 0)
    return has_validated, results


def validate_sample(sample):
    results = []

    if sample.scientific_name == "":
        results.append({'field': 'SCIENTIFIC_NAME',
                        'message': 'Failed regex check'})

    return results
