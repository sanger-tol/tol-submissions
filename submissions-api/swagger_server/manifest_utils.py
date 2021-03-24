from swagger_server.model import SubmissionsManifest, SubmissionsSample
import re


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
    return([])


def validate_against_ena_checklist(sample):
    results = []

    # Organism part exists
    if sample.organism_part == "":
        results.append({'field': 'ORGANISM_PART',
                        'message': 'Must not be empty'})

    # Lifestage is in list of allowed terms
    lifestage_terms = ["adult", "egg", "embryo", "gametophyte", "juvenile",
                       "larva", "not applicable", "not collected",
                       "not provided", "pupa", "spore-bearing structure",
                       "sporophyte", "vegetative cell", "vegetative structure",
                       "zygote"]
    if sample.lifestage.lower() not in lifestage_terms:
        results.append({'field': 'LIFESTAGE',
                        'message': 'Must be one of '+", ".join(lifestage_terms)})

    # Collected by exists
    if sample.collected_by == "":
        results.append({'field': 'COLLECTED_BY',
                        'message': 'Must not be empty'})

    # Collection date matches regex
    collection_date_pattern = re.compile(r"(^[0-9]{4}(-[0-9]{2}(-[0-9]{2}(T[0-9]{2}:[0-9]{2}(:[0-9]{2})?Z?([+-][0-9]{1,2})?)?)?)?(/[0-9]{4}(-[0-9]{2}(-[0-9]{2}(T[0-9]{2}:[0-9]{2}(:[0-9]{2})?Z?([+-][0-9]{1,2})?)?)?)?)?$)|(^not collected$)|(^not provided$)|(^restricted access$)")  # noqa
    if not collection_date_pattern.search(sample.date_of_collection):
        results.append({'field': 'COLLECTION_DATE',
                        'message': 'Must match specific pattern'})

    # Collection location (country) is in list of allowed countries
    allowed_countries = ["Afghanistan", "Albania", "Algeria", "American Samoa", "Andorra",
                         "Angola", "Anguilla", "Antarctica", "Antigua and Barbuda",
                         "Arctic Ocean", "Argentina", "Armenia", "Aruba",
                         "Ashmore and Cartier Islands", "Atlantic Ocean", "Australia",
                         "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Baker Island",
                         "Baltic Sea", "Bangladesh", "Barbados", "Bassas da India", "Belarus",
                         "Belgium", "Belize", "Benin", "Bermuda", "Bhutan", "Bolivia", "Borneo",
                         "Bosnia and Herzegovina", "Botswana", "Bouvet Island", "Brazil",
                         "British Virgin Islands", "Brunei", "Bulgaria", "Burkina Faso",
                         "Burundi", "Cambodia", "Cameroon", "Canada", "Cape Verde",
                         "Cayman Islands", "Central African Republic", "Chad", "Chile", "China",
                         "Christmas Island", "Clipperton Island", "Cocos Islands", "Colombia",
                         "Comoros", "Cook Islands", "Coral Sea Islands", "Costa Rica",
                         "Cote d'Ivoire", "Croatia", "Cuba", "Curacao", "Cyprus",
                         "Czech Republic", "Democratic Republic of the Congo", "Denmark",
                         "Djibouti", "Dominica", "Dominican Republic", "East Timor", "Ecuador",
                         "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia",
                         "Ethiopia", "Europa Island", "Falkland Islands (Islas Malvinas)",
                         "Faroe Islands", "Fiji", "Finland", "France", "French Guiana",
                         "French Polynesia", "French Southern and Antarctic Lands", "Gabon",
                         "Gambia", "Gaza Strip", "Georgia", "Germany", "Ghana", "Gibraltar",
                         "Glorioso Islands", "Greece", "Greenland", "Grenada", "Guadeloupe",
                         "Guam", "Guatemala", "Guernsey", "Guinea", "Guinea-Bissau", "Guyana",
                         "Haiti", "Heard Island and McDonald Islands", "Honduras", "Hong Kong",
                         "Howland Island", "Hungary", "Iceland", "India", "Indian Ocean",
                         "Indonesia", "Iran", "Iraq", "Ireland", "Isle of Man", "Israel", "Italy",
                         "Jamaica", "Jan Mayen", "Japan", "Jarvis Island", "Jersey",
                         "Johnston Atoll", "Jordan", "Juan de Nova Island", "Kazakhstan", "Kenya",
                         "Kerguelen Archipelago", "Kingman Reef", "Kiribati", "Kosovo", "Kuwait",
                         "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya",
                         "Liechtenstein", "Lithuania", "Luxembourg", "Macau", "Macedonia",
                         "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta",
                         "Marshall Islands", "Martinique", "Mauritania", "Mauritius", "Mayotte",
                         "Mediterranean Sea", "Mexico", "Micronesia", "Midway Islands", "Moldova",
                         "Monaco", "Mongolia", "Montenegro", "Montserrat", "Morocco",
                         "Mozambique", "Myanmar", "Namibia", "Nauru", "Navassa Island", "Nepal",
                         "Netherlands", "New Caledonia", "New Zealand", "Nicaragua", "Niger",
                         "Nigeria", "Niue", "Norfolk Island", "North Korea", "North Sea",
                         "Northern Mariana Islands", "Norway", "Oman", "Pacific Ocean",
                         "Pakistan", "Palau", "Palmyra Atoll", "Panama", "Papua New Guinea",
                         "Paracel Islands", "Paraguay", "Peru", "Philippines", "Pitcairn Islands",
                         "Poland", "Portugal", "Puerto Rico", "Qatar", "Republic of the Congo",
                         "Reunion", "Romania", "Ross Sea", "Russia", "Rwanda", "Saint Helena",
                         "Saint Kitts and Nevis", "Saint Lucia", "Saint Pierre and Miquelon",
                         "Saint Vincent and the Grenadines", "Samoa", "San Marino",
                         "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia",
                         "Seychelles", "Sierra Leone", "Singapore", "Sint Maarten", "Slovakia",
                         "Slovenia", "Solomon Islands", "Somalia", "South Africa",
                         "South Georgia and the South Sandwich Islands", "South Korea",
                         "Southern Ocean", "Spain", "Spratly Islands", "Sri Lanka", "Sudan",
                         "Suriname", "Svalbard", "Swaziland", "Sweden", "Switzerland", "Syria",
                         "Taiwan", "Tajikistan", "Tanzania", "Tasman Sea", "Thailand", "Togo",
                         "Tokelau", "Tonga", "Trinidad and Tobago", "Tromelin Island", "Tunisia",
                         "Turkey", "Turkmenistan", "Turks and Caicos Islands", "Tuvalu", "USA",
                         "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "Uruguay",
                         "Uzbekistan", "Vanuatu", "Venezuela", "Viet Nam", "Virgin Islands",
                         "Wake Island", "Wallis and Futuna", "West Bank", "Western Sahara",
                         "Yemen", "Zambia", "Zimbabwe", "not applicable", "not collected",
                         "not provided", "restricted access"]
    if sample.collection_country().lower() not in [x.lower() for x in allowed_countries]:
        results.append({'field': 'COLLECTION_LOCATION',
                        'message': 'Must be in the allowed list'})

    # Decimal latitude matches regex
    decimal_latitude_pattern = re.compile(r"(^.*[+-]?[0-9]+.?[0-9]*.*$)|(^not collected$)|(^not provided$)|(^restricted access$)")  # noqa
    if not decimal_latitude_pattern.search(sample.decimal_latitude):
        results.append({'field': 'DECIMAL_LATITUDE',
                        'message': 'Must match specific pattern'})

    # Decimal longitude matches regex
    decimal_longitude_pattern = re.compile(r"(^.*[+-]?[0-9]+.?[0-9]*.*$)|(^not collected$)|(^not provided$)|(^restricted access$)")  # noqa
    if not decimal_longitude_pattern.search(sample.decimal_latitude):
        results.append({'field': 'DECIMAL_LONGITUDE',
                        'message': 'Must match specific pattern'})

    # Collection region exists
    if sample.collection_region() == "":
        results.append({'field': 'COLLECTION_LOCATION',
                        'message': 'Collection region must be given'})

    # Identified by exists
    if sample.identified_by == "":
        results.append({'field': 'IDENTIFIED_BY',
                        'message': 'Must be given'})

    # Habitat
    if sample.habitat == "":
        results.append({'field': 'HABITAT',
                        'message': 'Must be given'})

    # Identifier affiliation exists
    if sample.identifier_affiliation == "":
        results.append({'field': 'IDENTIFIER_AFFILIATION',
                        'message': 'Must be given'})

    # Sex exists
    if sample.sex == "":
        results.append({'field': 'SEX',
                        'message': 'Must be given'})

    # Collector affiliation exists
    if sample.collector_affiliation == "":
        results.append({'field': 'COLLECTOR_AFFILIATION',
                        'message': 'Must be given'})

    # GAL is in list of allowed terms
    allowed_gals = ["Dalhousie University", "Earlham Institute",
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
                    "University of Vienna (Mollusc)"]
    if sample.GAL.lower() not in [x.lower() for x in allowed_gals]:
        results.append({'field': 'GAL',
                        'message': 'Must be in allowed list'})

    # Specimen voucher exists
    if sample.voucher_id == "":
        results.append({'field': 'VOUCHER_ID',
                        'message': 'Must be given'})

    # Specimen ID exists
    if sample.specimen_id == "":
        results.append({'field': 'SPECIMEN_ID',
                        'message': 'Must be given'})

    # GAL sample ID exists
    if sample.GAL_sample_id == "":
        results.append({'field': 'GAL_SAMPLE_ID',
                        'message': 'Must be given'})

    # if depth given, must match regex
    if sample.depth is not None:
        depth_pattern = re.compile(r"(0|((0\.)|([1-9][0-9]*\.?))[0-9]*)([Ee][+-]?[0-9]+)?")  # noqa
        if not depth_pattern.search(sample.depth):
            results.append({'field': 'DEPTH',
                            'message': 'Must match specific pattern'})

    # if elevation given, must match regex
    if sample.elevation is not None:
        elevation_pattern = re.compile(r"[+-]?(0|((0\.)|([1-9][0-9]*\.?))[0-9]*)([Ee][+-]?[0-9]+)?")  # noqa
        if not elevation_pattern.search(sample.elevation):
            results.append({'field': 'ELEVATION',
                            'message': 'Must match specific pattern'})

    return results


def validate_ena_submittable(sample):
    return([])
