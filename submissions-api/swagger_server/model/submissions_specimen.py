from .base import Base, db


class SubmissionsSpecimen(Base):
    __tablename__ = "specimen"
    specimen_id = db.Column(db.String(), primary_key=True)
    biosample_id = db.Column(db.String(), nullable=False)
