import { Sample } from './Sample';

export interface Specimen {
    specimenId: string;
    biospecimenId: string;
    samples: Sample[];
}
