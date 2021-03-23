from .base import Base, db


class SubmissionsManifest(Base):
    __tablename__ = "manifest"
    manifest_id = db.Column(db.Integer, primary_key=True)
    samples = db.relationship('SubmissionsSample', back_populates="manifest", lazy=False)

    def to_dict(cls):
        return {'manifestId': cls.manifest_id,
                'samples': cls.samples}
