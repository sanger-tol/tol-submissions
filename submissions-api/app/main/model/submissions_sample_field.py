# SPDX-FileCopyrightText: 2021 Genome Research Ltd.
#
# SPDX-License-Identifier: MIT

from .base import Base, db


class SubmissionsSampleField(Base):
    __tablename__ = 'sample_field'
    sample_id = db.Column(db.Integer, db.ForeignKey('sample.sample_id'), primary_key=True)
    sample = db.relationship('SubmissionsSample', back_populates='sample_fields',
                             uselist=False, foreign_keys=[sample_id])
    name = db.Column(db.String(), nullable=False, primary_key=True)
    value = db.Column(db.String(), nullable=False)
