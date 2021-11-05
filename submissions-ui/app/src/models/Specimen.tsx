{/*
SPDX-FileCopyrightText: 2021 Genome Research Ltd.

SPDX-License-Identifier: MIT
*/}

import { Sample } from './Sample';

export interface Specimen {
    specimenId: string;
    biospecimenId: string;
    samples: Sample[];
}
