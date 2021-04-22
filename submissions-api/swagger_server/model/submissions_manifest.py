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
