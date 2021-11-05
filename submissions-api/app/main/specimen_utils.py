# SPDX-FileCopyrightText: 2021 Genome Research Ltd.
#
# SPDX-License-Identifier: MIT

from main.model.submissions_specimen import SubmissionsSpecimen

import requests
import os


def process_specimen_sts(specimen_sts):
    specimen = SubmissionsSpecimen()

    specimen.biosample_accession = specimen_sts["bio_specimen_id"]
    specimen.specimen_id = specimen_sts["specimen_id"]

    return specimen


def get_specimen_sts(specimen_id):
    response = requests.get(
        os.environ["STS_URL"] + "/specimens",
        params={'specimen_id': specimen_id},
        headers={'Project': 'ALL',
                 'Authorization': os.getenv("STS_API_KEY")}
    )
    if response.status_code != 200:
        return None

    data = response.json()["data"]["list"]
    if len(data) != 1:
        return None

    return process_specimen_sts(data[0])


def get_biospecimen_sts(biospecimen_id):
    response = requests.get(
        os.environ["STS_URL"] + "/specimens",
        params={'bio_specimen_id': biospecimen_id},
        headers={'Project': 'ALL',
                 'Authorization': os.getenv("STS_API_KEY")}
    )
    if response.status_code != 200:
        return None

    data = response.json()["data"]["list"]
    if len(data) != 1:
        return None

    return process_specimen_sts(data[0])
