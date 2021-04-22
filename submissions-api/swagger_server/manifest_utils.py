from swagger_server.model import db, SubmissionsManifest, SubmissionsSample, \
    SubmissionsSpecimen, SubmissionsSampleField
from swagger_server.xml_utils import build_bundle_sample_xml, build_submission_xml
import re
import os
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
import logging


def create_manifest_from_json(json, user):
    manifest = SubmissionsManifest()
    manifest.user = user
    if "projectName" in json:
        manifest.project_name = json["projectName"]
    if "stsManifestId" in json:
        manifest.sts_manifest_id = json["stsManifestId"]
    ignore_fields = []
    for s in json["samples"]:
        sample = SubmissionsSample()
        sample.manifest = manifest
        sample.row = s.get('row')
        ignore_fields.append('row')
        # All named fields
        for field in SubmissionsSample.all_fields:
            value = s.get(field["field_name"])
            setattr(sample, field["python_name"], value)
            ignore_fields.append(field["field_name"])

        # Extra fields
        for field_name in s:
            if field_name not in ignore_fields:
                sample_field = SubmissionsSampleField()
                sample_field.sample = sample
                sample_field.name = field_name
                sample_field.value = s.get(field_name)

    return manifest


def validate_manifest(manifest, full=True):
    results = []
    number_of_errors = 0
    for sample in manifest.samples:
        if full:
            sample_results = validate_sample(sample)
        else:
            sample_results = validate_required_fields(sample)
        results.append({'row': sample.row,
                        'results': sample_results})
        number_of_errors += len(sample_results)
    return number_of_errors, results


def validate_required_fields(sample):
    results = []
    for field in sample.all_fields:
        if field["required"] and getattr(sample, field["python_name"]) is None:
            results.append({'field': field["field_name"],
                            'message': 'A value must be given',
                            'severity': 'ERROR'})
    return results


def validate_sample(sample):
    results = []

    results += validate_required_fields(sample)

    # Validate ToLID species exists
    # Validate SCIENTIFIC_NAME, FAMILY, GENUS, ORDER
    results += validate_against_tolid(sample)

    # Validate against ENA checklist
    results += validate_against_ena_checklist(sample)

    # Validate taxon is ENA submittable
    results += validate_ena_submittable(sample)

    return results


def validate_against_tolid(sample):
    results = []
    response = requests.get(os.environ['TOLID_URL'] + '/species/'
                            + str(sample.taxonomy_id))
    if (response.status_code == 404):
        results.append({'field': 'TAXON_ID',
                        'message': 'Species not known in the ToLID service',
                        'severity': 'WARNING'})
        return results

    if (response.status_code != 200):
        results.append({'field': 'TAXON_ID',
                        'message': 'Communication failed with the ToLID service: status code '
                        + str(response.status_code),
                        'severity': 'ERROR'})
        return results

    data = response.json()[0]

    # Does the SCIENTIFIC_NAME match?
    if data['scientificName'] != sample.scientific_name:
        results.append({'field': 'SCIENTIFIC_NAME',
                        'message': 'Does not match that in the ToLID service (expecting '
                        + data['scientificName'] + ')',
                        'severity': 'ERROR'})

    # Does the GENUS match?
    if data['genus'] != sample.genus:
        results.append({'field': 'GENUS',
                        'message': 'Does not match that in the ToLID service (expecting '
                        + data['genus'] + ')',
                        'severity': 'ERROR'})

    # Does the FAMILY match?
    if data['family'] != sample.family:
        results.append({'field': 'FAMILY',
                        'message': 'Does not match that in the ToLID service (expecting '
                        + data['family'] + ')',
                        'severity': 'ERROR'})

    # Does the ORDER match?
    if data['order'] != sample.order_or_group:
        results.append({'field': 'ORDER_OR_GROUP',
                        'message': 'Does not match that in the ToLID service (expecting '
                        + data['order'] + ')',
                        'severity': 'ERROR'})

    return(results)


def validate_against_ena_checklist(sample):
    results = []

    ena_fields = sample.to_ena_dict()

    ena_checklist = get_ena_checklist()

    for check in ena_checklist:
        fieldName = check
        if "field" in ena_checklist[check]:
            fieldName = ena_checklist[check]["field"]

        # Check mandatory fields
        if ena_checklist[check]["mandatory"] and check not in ena_fields:
            results.append({'field': fieldName,
                            'message': 'Must be given',
                            'severity': 'ERROR'})
            continue
        if ena_checklist[check]["mandatory"] and ena_fields[check]["value"] == "":
            results.append({'field': fieldName,
                            'message': 'Must not be empty',
                            'severity': 'ERROR'})
            continue

        # Check against regex
        if "regex" in ena_checklist[check] and check in ena_fields:
            compiled_re = re.compile(ena_checklist[check]["regex"])
            if not compiled_re.search(ena_fields[check]["value"]):
                results.append({'field': fieldName,
                                'message': 'Must match specific pattern',
                                'severity': 'ERROR'})

        # Check against allowed values
        if "allowed_values" in ena_checklist[check] and check in ena_fields:
            if ena_fields[check]["value"].lower() not in \
                    [x.lower() for x in ena_checklist[check]["allowed_values"]]:
                results.append({'field': fieldName,
                                'message': 'Must be in allowed values',
                                'severity': 'ERROR'})

    return results


def get_ena_checklist():
    return {"organism part": {"mandatory": True,
                              "field": "ORGANISM_PART"},
            "lifestage": {"mandatory": True,
                          "field": "LIFESTAGE",
                          "allowed_values": ["adult", "egg", "embryo", "gametophyte", "juvenile",
                                             "larva", "not applicable", "not collected",
                                             "not provided", "pupa", "spore-bearing structure",
                                             "sporophyte", "vegetative cell",
                                             "vegetative structure", "zygote"]},
            "project name": {"mandatory": True},
            # "tolid": {"mandatory": True,
            #           "regex": r"(^[a-z]{1}[A-Z]{1}[a-z]{2}[A-Z]{1}[a-z]{2}[0-9]*$)|(^[a-z]{2}[A-Z]{1}[a-z]{2}[A-Z]{1}[a-z]{3}[0-9]*$)"},  # noqa
            "collected by": {"mandatory": True,
                             "field": "COLLECTED_BY"},
            "collection date": {"mandatory": True,
                                "field": "DATE_OF_COLLECTION",
                                "regex": r"(^[0-9]{4}(-[0-9]{2}(-[0-9]{2}(T[0-9]{2}:[0-9]{2}(:[0-9]{2})?Z?([+-][0-9]{1,2})?)?)?)?(/[0-9]{4}(-[0-9]{2}(-[0-9]{2}(T[0-9]{2}:[0-9]{2}(:[0-9]{2})?Z?([+-][0-9]{1,2})?)?)?)?)?$)|(^not collected$)|(^not provided$)|(^restricted access$)"},  # noqa
            "geographic location (country and/or sea)": {
                "mandatory": True,
                "field": "COLLECTION_LOCATION",
                "allowed_values": ["Afghanistan", "Albania", "Algeria", "American Samoa",
                                   "Andorra", "Angola", "Anguilla", "Antarctica",
                                   "Antigua and Barbuda", "Arctic Ocean", "Argentina", "Armenia",
                                   "Aruba", "Ashmore and Cartier Islands", "Atlantic Ocean",
                                   "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain",
                                   "Baker Island", "Baltic Sea", "Bangladesh", "Barbados",
                                   "Bassas da India", "Belarus", "Belgium", "Belize", "Benin",
                                   "Bermuda", "Bhutan", "Bolivia", "Borneo",
                                   "Bosnia and Herzegovina", "Botswana", "Bouvet Island",
                                   "Brazil", "British Virgin Islands", "Brunei", "Bulgaria",
                                   "Burkina Faso", "Burundi", "Cambodia", "Cameroon", "Canada",
                                   "Cape Verde", "Cayman Islands", "Central African Republic",
                                   "Chad", "Chile", "China", "Christmas Island",
                                   "Clipperton Island", "Cocos Islands", "Colombia", "Comoros",
                                   "Cook Islands", "Coral Sea Islands", "Costa Rica",
                                   "Cote d'Ivoire", "Croatia", "Cuba", "Curacao", "Cyprus",
                                   "Czech Republic", "Democratic Republic of the Congo",
                                   "Denmark", "Djibouti", "Dominica", "Dominican Republic",
                                   "East Timor", "Ecuador", "Egypt", "El Salvador",
                                   "Equatorial Guinea", "Eritrea", "Estonia", "Ethiopia",
                                   "Europa Island", "Falkland Islands (Islas Malvinas)",
                                   "Faroe Islands", "Fiji", "Finland", "France", "French Guiana",
                                   "French Polynesia", "French Southern and Antarctic Lands",
                                   "Gabon", "Gambia", "Gaza Strip", "Georgia", "Germany",
                                   "Ghana", "Gibraltar", "Glorioso Islands", "Greece",
                                   "Greenland", "Grenada", "Guadeloupe", "Guam", "Guatemala",
                                   "Guernsey", "Guinea", "Guinea-Bissau", "Guyana", "Haiti",
                                   "Heard Island and McDonald Islands", "Honduras", "Hong Kong",
                                   "Howland Island", "Hungary", "Iceland", "India",
                                   "Indian Ocean", "Indonesia", "Iran", "Iraq", "Ireland",
                                   "Isle of Man", "Israel", "Italy", "Jamaica", "Jan Mayen",
                                   "Japan", "Jarvis Island", "Jersey", "Johnston Atoll",
                                   "Jordan", "Juan de Nova Island", "Kazakhstan", "Kenya",
                                   "Kerguelen Archipelago", "Kingman Reef", "Kiribati", "Kosovo",
                                   "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon",
                                   "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania",
                                   "Luxembourg", "Macau", "Macedonia", "Madagascar", "Malawi",
                                   "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands",
                                   "Martinique", "Mauritania", "Mauritius", "Mayotte",
                                   "Mediterranean Sea", "Mexico", "Micronesia", "Midway Islands",
                                   "Moldova", "Monaco", "Mongolia", "Montenegro", "Montserrat",
                                   "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauru",
                                   "Navassa Island", "Nepal", "Netherlands", "New Caledonia",
                                   "New Zealand", "Nicaragua", "Niger", "Nigeria", "Niue",
                                   "Norfolk Island", "North Korea", "North Sea",
                                   "Northern Mariana Islands", "Norway", "Oman", "Pacific Ocean",
                                   "Pakistan", "Palau", "Palmyra Atoll", "Panama",
                                   "Papua New Guinea", "Paracel Islands", "Paraguay", "Peru",
                                   "Philippines", "Pitcairn Islands", "Poland", "Portugal",
                                   "Puerto Rico", "Qatar", "Republic of the Congo", "Reunion",
                                   "Romania", "Ross Sea", "Russia", "Rwanda", "Saint Helena",
                                   "Saint Kitts and Nevis", "Saint Lucia",
                                   "Saint Pierre and Miquelon",
                                   "Saint Vincent and the Grenadines", "Samoa", "San Marino",
                                   "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia",
                                   "Seychelles", "Sierra Leone", "Singapore", "Sint Maarten",
                                   "Slovakia", "Slovenia", "Solomon Islands", "Somalia",
                                   "South Africa",
                                   "South Georgia and the South Sandwich Islands", "South Korea",
                                   "Southern Ocean", "Spain", "Spratly Islands", "Sri Lanka",
                                   "Sudan", "Suriname", "Svalbard", "Swaziland", "Sweden",
                                   "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania",
                                   "Tasman Sea", "Thailand", "Togo", "Tokelau", "Tonga",
                                   "Trinidad and Tobago", "Tromelin Island", "Tunisia",
                                   "Turkey", "Turkmenistan", "Turks and Caicos Islands",
                                   "Tuvalu", "USA", "Uganda", "Ukraine", "United Arab Emirates",
                                   "United Kingdom", "Uruguay", "Uzbekistan", "Vanuatu",
                                   "Venezuela", "Viet Nam", "Virgin Islands", "Wake Island",
                                   "Wallis and Futuna", "West Bank", "Western Sahara", "Yemen",
                                   "Zambia", "Zimbabwe", "not applicable", "not collected",
                                   "not provided", "restricted access"]},
                "geographic location (latitude)": {"mandatory": True,
                                                   "field": "DECIMAL_LATITUDE",
                                                   "regex": r"(^.*[+-]?[0-9]+.?[0-9]*.*$)|(^not collected$)|(^not provided$)|(^restricted access$)"},  # noqa
                "geographic location (longitude)": {"mandatory": True,
                                                    "field": "DECIMAL_LONGITUDE",
                                                    "regex": r"(^.*[+-]?[0-9]+.?[0-9]*.*$)|(^not collected$)|(^not provided$)|(^restricted access$)"},  # noqa
                "geographic location (region and locality)": {"mandatory": True,
                                                              "field": "COLLECTION_LOCATION"},
                "identified_by": {"mandatory": True,
                                  "field": "IDENTIFIED_BY"},
                "geographic location (depth)": {"mandatory": False,
                                                "field": "DEPTH",
                                                "regex": r"(0|((0\.)|([1-9][0-9]*\.?))[0-9]*)([Ee][+-]?[0-9]+)?"},  # noqa
                "geographic location (elevation)": {"mandatory": False,
                                                    "field": "ELEVATION",
                                                    "regex": r"[+-]?(0|((0\.)|([1-9][0-9]*\.?))[0-9]*)([Ee][+-]?[0-9]+)?"},  # noqa
                "habitat": {"mandatory": True,
                            "field": "HABITAT"},
                "identifier_affiliation": {"mandatory": True,
                                           "field": "IDENTIFIER_AFFILIATION"},
                "sample derived from": {"mandatory": False,
                                        "regex": r"(^[ESD]R[SR]\d{6,}(,[ESD]R[SR]\d{6,})*$)|(^SAM[END][AG]?\d+(,SAM[END][AG]?\d+)*$)|(^EGA[NR]\d{11}(,EGA[NR]\d{11})*$)|(^[ESD]R[SR]\d{6,}-[ESD]R[SR]\d{6,}$)|(^SAM[END][AG]?\d+-SAM[END][AG]?\d+$)|(^EGA[NR]\d{11}-EGA[NR]\d{11}$)"},  # noqa
                "sample same as": {"mandatory": False,
                                   "regex": r"(^[ESD]RS\d{6,}(,[ESD]RS\d{6,})*$)|(^SAM[END][AG]?\d+(,SAM[END][AG]?\d+)*$)|(^EGAN\d{11}(,EGAN\d{11})*$)"},  # noqa
                "sample symbiont of": {"mandatory": False,
                                       "regex": r"(^[ESD]RS\d{6,}$)|(^SAM[END][AG]?\d+$)|(^EGAN\d{11}$)"},  # noqa
                "sex": {"mandatory": True,
                        "field": "SEX"},
                "relationship": {"mandatory": False,
                                 "field": "RELATIONSHIP"},
                "symbiont": {"mandatory": False,
                             "field": "SYMBIONT",
                             "allowed_options": ['N', 'Y']},
                "collecting institution": {"mandatory": True,
                                           "field": "COLLECTOR_AFFILIATION"},
                "GAL": {"mandatory": True,
                        "field": "GAL",
                        "allowed_values": [
                            "Dalhousie University", "Earlham Institute",
                            "Geomar Helmholtz Centre", "Marine Biological Association",
                            "Natural History Museum", "Nova Southeastern University",
                            "Portland State University", "Queen Mary University of London",
                            "Royal Botanic Garden Edinburgh", "Royal Botanic Gardens Kew",
                            "Sanger Institute", "Senckenberg Research Institute",
                            "The Sainsbury Laboratory", "University of British Columbia",
                            "University of California", "University of Cambridge",
                            "University of Derby", "University of Edinburgh",
                            "University of Oregon", "University of Oxford"
                            "University of Rhode Island", "University of Vienna (Cephalopod)",
                            "University of Vienna (Mollusc)"]},
                "specimen_voucher": {"mandatory": True,
                                     "field": "VOUCHER_ID"},
                "specimen_id": {"mandatory": True,
                                "field": "SPECIMEN_ID"},
                "GAL_sample_id": {"mandatory": True,
                                  "field": "GAL_SAMPLE_ID"},
                "culture_or_strain_id": {"mandatory": False,
                                         "field": "CULTURE_OR_STRAIN_ID"}}


def validate_ena_submittable(sample):
    # https://www.ebi.ac.uk/ena/taxonomy/rest/tax-id/9606
    #
    # {
    # "taxId" : "9606",
    #  "scientificName" : "Homo sapiens",
    #  "commonName" : "human",
    #  "formalName" : "true",
    #  "rank" : "species",
    #  "division" : "HUM",
    #  "lineage" : "Eukaryota; Metazoa; Chordata; Craniata; Vertebrata; Euteleostomi;
    #               Mammalia; Eutheria; Euarchontoglires; Primates; Haplorrhini; Catarrhini;
    #               Hominidae; Homo; ",
    #  "geneticCode" : "1",
    #  "mitochondrialGeneticCode" : "2",
    #  "submittable" : "true"
    # }
    results = []

    response = requests.get('https://www.ebi.ac.uk/ena/taxonomy/rest/tax-id/'
                            + str(sample.taxonomy_id))
    if (response.status_code != 200):
        results.append({'field': 'TAXON_ID',
                        'message': 'Communication with ENA has failed with status code '
                        + str(response.status_code),
                        'severity': 'ERROR'})
        return results

    # Might be an unknown TAX_ID
    if response.text == "No results.":
        results.append({'field': 'TAXON_ID',
                        'message': 'Is not known at ENA',
                        'severity': 'ERROR'})
        return results
    data = response.json()

    # ENA submittable?
    if data['submittable'] != "true":
        results.append({'field': 'TAXON_ID',
                        'message': 'Is not ENA submittable',
                        'severity': 'ERROR'})

    if data['scientificName'] != sample.scientific_name:
        results.append({'field': 'SCIENTIFIC_NAME',
                        'message': 'Must match ENA (expected ' + data['scientificName'] + ')',
                        'severity': 'ERROR'})

    return(results)


def set_relationships_for_manifest(manifest):
    error_count = 0
    results = []
    for sample in manifest.samples:
        set_relationships_for_sample(sample)

    # Any with no relationship set need a new specimen submitting to ENA
    new_specimen_samples = []
    seen = set()
    for sample in manifest.samples:
        if sample.sample_same_as is None and sample.sample_derived_from is None:
            if sample.specimen_id not in seen:
                seen.add(sample.specimen_id)
                new_specimen_samples.append(sample)

    if len(new_specimen_samples) > 0:
        specimen_manifest = SubmissionsManifest()
        specimen_manifest.user = manifest.user
        for sample in new_specimen_samples:
            specimen_sample = make_specimen_sample(sample)
            specimen_sample.manifest = specimen_manifest
            db.session.add(specimen_sample)
        db.session.add(specimen_manifest)
        db.session.commit()
        # Submit this specimen_manifest to ENA
        error_count, results = generate_ena_ids_for_manifest(specimen_manifest)

        if error_count == 0:
            # Save the specimens
            for specimen_sample in specimen_manifest.samples:
                specimen = SubmissionsSpecimen()
                specimen.specimen_id = specimen_sample.specimen_id
                specimen.biosample_accession = specimen_sample.biosample_accession
                db.session.add(specimen)
                db.session.commit()

            # Update relationships to pick up these new ones
            for sample in manifest.samples:
                set_relationships_for_sample(sample)
                db.session.commit()

    return error_count, results


def set_relationships_for_sample(sample):
    # Look up previous specimens
    specimen = db.session.query(SubmissionsSpecimen) \
        .filter(SubmissionsSpecimen.specimen_id == sample.specimen_id) \
        .one_or_none()

    if specimen is None:
        # Look up in BioSamples
        pass

    if specimen is not None:
        if sample.organism_part == "WHOLE_ORGANISM":
            sample.sample_same_as = specimen.biosample_accession
        else:
            sample.sample_derived_from = specimen.biosample_accession


def make_specimen_sample(sample):
    specimen_sample = SubmissionsSample()
    specimen_sample.row = sample.row
    specimen_sample.specimen_id = sample.specimen_id
    specimen_sample.taxonomy_id = sample.taxonomy_id
    specimen_sample.scientific_name = sample.scientific_name
    specimen_sample.family = sample.family
    specimen_sample.genus = sample.genus
    specimen_sample.order_or_group = sample.order_or_group
    specimen_sample.common_name = sample.common_name
    specimen_sample.lifestage = sample.lifestage
    specimen_sample.sex = sample.sex
    specimen_sample.organism_part = "WHOLE_ORGANISM"
    specimen_sample.GAL = sample.GAL
    specimen_sample.GAL_sample_id = "NOT_PROVIDED"
    specimen_sample.collected_by = sample.collected_by
    specimen_sample.collector_affiliation = sample.collector_affiliation
    specimen_sample.date_of_collection = sample.date_of_collection
    specimen_sample.collection_location = sample.collection_location
    specimen_sample.decimal_latitude = sample.decimal_latitude
    specimen_sample.decimal_longitude = sample.decimal_longitude
    specimen_sample.habitat = sample.habitat
    specimen_sample.identified_by = sample.identified_by
    specimen_sample.identifier_affiliation = sample.identifier_affiliation
    specimen_sample.voucher_id = sample.voucher_id
    specimen_sample.elevation = sample.elevation
    specimen_sample.depth = sample.depth
    specimen_sample.relationship = sample.relationship
    specimen_sample.symbiont = sample.symbiont
    specimen_sample.culture_or_strain_id = sample.culture_or_strain_id

    specimen_sample.tolid = sample.tolid
    return specimen_sample


def generate_ids_for_manifest(manifest):
    # ToLIDs
    error_count, results = generate_tolids_for_manifest(manifest)

    if error_count > 0:
        # Something has gone wrong with the ToLID assignment
        return error_count, results

    # sampleSameAs, sampleDerivedFrom (specimens)
    error_count, results = set_relationships_for_manifest(manifest)
    if error_count > 0:
        # Something has gone wrong with the ENA assignment
        return error_count, results

    # ENA IDs
    error_count, results = generate_ena_ids_for_manifest(manifest)
    if error_count > 0:
        # Something has gone wrong with the ENA assignment
        return error_count, results

    db.session.commit()
    return 0, []


def generate_tolids_for_manifest(manifest):
    results = []
    error_count = 0
    # ToLIDs
    # List of taxon-specimen pairs
    taxon_specimens = []
    for sample in manifest.samples:
        taxon_specimen = {"taxonomyId": sample.taxonomy_id,
                          "specimenId": sample.specimen_id}
        if taxon_specimen not in taxon_specimens:
            taxon_specimens.append(taxon_specimen)

    response = requests.post(os.environ['TOLID_URL'] + '/tol-ids',
                             json=taxon_specimens,
                             headers={"api-key": os.getenv("TOLID_API_KEY")})
    if (response.status_code != 200):
        results.append({"row": sample.row,
                        "results": [{'field': 'TAXON_ID',
                                     'message': 'Cannot connect to ToLID service',
                                     'severity': 'ERROR'}]})
        return 1, results

    for tolid in response.json():
        samples_to_update = db.session.query(SubmissionsSample) \
            .filter(SubmissionsSample.manifest == manifest) \
            .filter(SubmissionsSample.specimen_id == tolid["specimen"]["specimenId"]) \
            .filter(SubmissionsSample.taxonomy_id == tolid["species"]["taxonomyId"]) \
            .all()
        for sample_to_update in samples_to_update:
            if "tolId" in tolid:
                sample_to_update.tolid = tolid["tolId"]
            else:
                # ToLID not been assigned - a request must have been generated
                results.append({"row": sample_to_update.row,
                                "results": [{'field': 'TAXON_ID',
                                             'message': 'A ToLID has not been generated',
                                             'severity': 'WARNING'}]})
                error_count += 1

    if error_count > 0:
        return error_count, results

    # Needs commiting elsewhere
    return 0, []


def generate_ena_ids_for_manifest(manifest):
    results = []
    error_count = 0
    bundle_xml_file = build_bundle_sample_xml(manifest)
    submission_xml_file = build_submission_xml(manifest)
    xml_files = [("SAMPLE", open(bundle_xml_file, "rb")),
                 ("SUBMISSION", open(submission_xml_file, "rb"))]
    response = requests.post(os.environ['ENA_URL'] + '/ena/submit/drop-box/submit/',
                             files=xml_files,
                             auth=HTTPBasicAuth(os.environ['ENA_USERNAME'],
                                                os.environ['ENA_PASSWORD']))

    if (response.status_code != 200):
        results.append({"row": 1,
                        "results": [{'field': 'TAXON_ID',
                                     'message': 'Cannot connect to ENA service (status code '
                                     + str(response.status_code) + ')',
                                    'severity': 'ERROR'}]})
        return 1, results

    if not assign_ena_ids(manifest, response.text):
        results.append({"row": 1,
                        "results": [{'field': 'TAXON_ID',
                                     'message': 'Error returned from ENA service',
                                     'severity': 'ERROR'}]})
        return 1, results
    return error_count, results


def assign_ena_ids(manifest, xml):
    try:
        tree = ET.fromstring(xml)
    except ET.ParseError:
        #  message = " Unrecognized response from ENA - " + str(
        #    xml) + " Please try again later, if it persists contact admins"
        return False

    success_status = tree.get('success')
    if success_status == 'false':
        manifest.submission_status = False
        msg = ""
        error_blocks = tree.find('MESSAGES').findall('ERROR')
        for error in error_blocks:
            msg += error.text + "<br>"
        if not msg:
            msg = "Undefined error"
        # status = {"status": "error", "msg": msg}
        # print(status)
        logging.warning(msg)
        for child in tree.iter():
            if child.tag == 'SAMPLE':
                sample_id = child.get('alias')
                sample = db.session.query(SubmissionsSample) \
                    .filter(SubmissionsSample.manifest == manifest) \
                    .filter(SubmissionsSample.sample_id == sample_id) \
                    .one_or_none()
                sample.submission_error = msg
        return False
    else:
        manifest.submission_status = True
        return assign_biosample_accessions(manifest, xml)


def assign_biosample_accessions(manifest, xml):
    tree = ET.fromstring(xml)
    submission_accession = tree.find('SUBMISSION').get('accession')
    for child in tree.iter():
        if child.tag == 'SAMPLE':
            sample_id = child.get('alias')
            sra_accession = child.get('accession')
            biosample_accession = child.find('EXT_ID').get('accession')
            sample = db.session.query(SubmissionsSample) \
                .filter(SubmissionsSample.manifest == manifest) \
                .filter(SubmissionsSample.sample_id == sample_id) \
                .one_or_none()
            if sample is None:
                continue
            sample.biosample_accession = biosample_accession
            sample.sra_accession = sra_accession
            sample.submission_accession = submission_accession
    return True
