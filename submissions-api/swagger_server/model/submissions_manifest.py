from .base import Base, db


class SubmissionsManifest(Base):
    __tablename__ = "manifest"
    manifest_id = db.Column(db.Integer, primary_key=True)
    samples = db.relationship('SubmissionsSample', back_populates="manifest", lazy=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    user = db.relationship("SubmissionsUser", uselist=False, foreign_keys=[created_by])
    submission_status = db.Column(db.Boolean, nullable=True)

    def to_dict(cls):
        return {'manifestId': cls.manifest_id,
                'samples': cls.samples,
                'submissionStatus': cls.submission_status}
