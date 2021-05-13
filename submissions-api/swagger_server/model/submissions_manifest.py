from .base import Base, db


class SubmissionsManifest(Base):
    __tablename__ = "manifest"
    manifest_id = db.Column(db.Integer, primary_key=True)
    samples = db.relationship('SubmissionsSample', back_populates="manifest",
                              lazy=False, order_by='SubmissionsSample.row')
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    user = db.relationship("SubmissionsUser", uselist=False, foreign_keys=[created_by])
    submission_status = db.Column(db.Boolean, nullable=True)
    project_name = db.Column(db.String(), nullable=False, default="ToL")
    sts_manifest_id = db.Column(db.String(), nullable=True)
    excel_file = db.Column(db.String(), nullable=True)

    target_rack_plate_tube_wells = set()
    duplicate_rack_plate_tube_wells = []
    target_specimen_taxons = {}
    whole_organisms = set()
    duplicate_whole_organisms = []

    def reset_trackers(self):
        # Target rack/plate and tube/well ids
        all = []
        for sample in self.samples:
            if not sample.is_symbiont() and sample.rack_or_plate_id is not None \
                    and sample.tube_or_well_id is not None:
                concatenated = sample.rack_or_plate_id + '/' + sample.tube_or_well_id
                all.append(concatenated)
        self.target_rack_plate_tube_wells = set()
        seen_add = self.target_rack_plate_tube_wells.add
        # adds all elements it doesn't know yet to seen and all other to seen_twice
        self.duplicate_rack_plate_tube_wells = set(x for x in all if x in
                                                   self.target_rack_plate_tube_wells
                                                   or seen_add(x))
        # Target specimen/taxons
        self.target_specimen_taxons = {}
        for sample in self.samples:
            if not sample.is_symbiont() and sample.specimen_id is not None \
                    and sample.taxonomy_id is not None:
                # Only add the first one
                if sample.specimen_id not in self.target_specimen_taxons:
                    self.target_specimen_taxons[sample.specimen_id] = sample.taxonomy_id

        # Whole organisms
        all = []
        for sample in self.samples:
            if sample.organism_part == "WHOLE_ORGANISM":
                all.append(sample.specimen_id)
        self.whole_organisms = set()
        seen_add = self.whole_organisms.add
        # adds all elements it doesn't know yet to seen and all other to seen_twice
        self.duplicate_whole_organisms = set(x for x in all if x in
                                             self.whole_organisms
                                             or seen_add(x))

    def to_dict(cls):
        return {'manifestId': cls.manifest_id,
                'projectName': cls.project_name,
                'stsManifestId': cls.sts_manifest_id,
                'samples': cls.samples,
                'submissionStatus': cls.submission_status}

    def to_dict_short(cls):
        return {'manifestId': cls.manifest_id,
                'projectName': cls.project_name,
                'stsManifestId': cls.sts_manifest_id,
                'submissionStatus': cls.submission_status,
                'createdAt': cls.created_at,
                'numberOfSamples': len(cls.samples),
                'user': cls.user}
