from swagger_server.model import db, SubmissionsManifest, SubmissionsSample
import re
import os
import requests


def create_manifest_from_json(samples, user):
    manifest = SubmissionsManifest()
    manifest.user = user
    for s in samples:
        sample = SubmissionsSample()
        sample.manifest = manifest
        sample.row = s.get('row')
        sample.specimen_id = s.get('SPECIMEN_ID')
        sample.taxonomy_id = s.get('TAXON_ID')
        sample.scientific_name = s.get('SCIENTIFIC_NAME')
        sample.family = s.get('FAMILY')
        sample.genus = s.get('GENUS')
        sample.order_or_group = s.get('ORDER_OR_GROUP')
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
                        'message': 'Species not known in the ToLID service'})
        return results

    if (response.status_code != 200):
        results.append({'field': 'TAXON_ID',
                        'message': 'Communication failed with the ToLID service: status code '
                        + str(response.status_code)})
        return results

    data = response.json()[0]

    # Does the SCIENTIFIC_NAME match?
    if data['scientificName'] != sample.scientific_name:
        results.append({'field': 'SCIENTIFIC_NAME',
                        'message': 'Does not match that in the ToLID service (expecting '
                        + data['scientificName'] + ')'})

    # Does the GENUS match?
    if data['genus'] != sample.genus:
        results.append({'field': 'GENUS',
                        'message': 'Does not match that in the ToLID service (expecting '
                        + data['genus'] + ')'})

    # Does the FAMILY match?
    if data['family'] != sample.family:
        results.append({'field': 'FAMILY',
                        'message': 'Does not match that in the ToLID service (expecting '
                        + data['family'] + ')'})

    # Does the ORDER match?
    if data['order'] != sample.order_or_group:
        results.append({'field': 'ORDER_OR_GROUP',
                        'message': 'Does not match that in the ToLID service (expecting '
                        + data['order'] + ')'})

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
                            'message': 'Must be given'})
            continue
        if ena_checklist[check]["mandatory"] and ena_fields[check]["value"] == "":
            results.append({'field': fieldName,
                            'message': 'Must not be empty'})
            continue

        # Check against regex
        if "regex" in ena_checklist[check] and check in ena_fields:
            compiled_re = re.compile(ena_checklist[check]["regex"])
            if not compiled_re.search(ena_fields[check]["value"]):
                results.append({'field': fieldName,
                                'message': 'Must match specific pattern'})

        # Check against allowed values
        if "allowed_values" in ena_checklist[check] and check in ena_fields:
            if ena_fields[check]["value"].lower() not in \
                    [x.lower() for x in ena_checklist[check]["allowed_values"]]:
                results.append({'field': fieldName,
                                'message': 'Must be in allowed values'})

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
                        + str(response.status_code)})
        return results

    # Might be an unknown TAX_ID
    if response.text == "No results.":
        results.append({'field': 'TAXON_ID',
                        'message': 'Is not known at ENA'})
        return results
    data = response.json()

    # ENA submittable?
    if data['submittable'] != "true":
        results.append({'field': 'TAXON_ID',
                        'message': 'Is not ENA submittable'})

    if data['scientificName'] != sample.scientific_name:
        results.append({'field': 'SCIENTIFIC_NAME',
                        'message': 'Must match ENA (expected ' + data['scientificName'] + ')'})

    return(results)


def generate_ids_for_manifest(manifest):
    # ToLIDs
    results = generate_tolids_for_manifest(manifest)

    if len(results) > 0:
        # Something has gone wrong with the ToLID assignment
        return results

    # ENA IDs
    generate_ena_ids_for_manifest(manifest)

    db.session.commit()


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
                             data=taxon_specimens,
                             headers={"api-key": os.getenv("TOLID_API_KEY")})
    if (response.status_code != 200):
        results.append({"row": sample.row,
                        "results": [{'field': 'TAXON_ID',
                                     'message': 'Cannot connect to ToLID service'}]})
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
                                            'message': 'A ToLID has not been generated'}]})
                error_count += 1

    if error_count > 0:
        return error_count, results

    # Needs commiting elsewhere
    return 0, []


def generate_ena_ids_for_manifest(manifest):
    return 0, []
