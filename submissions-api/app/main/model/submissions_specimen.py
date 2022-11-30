# SPDX-FileCopyrightText: 2021 Genome Research Ltd.
#
# SPDX-License-Identifier: MIT

from .base import Base, db


class SubmissionsSpecimen(Base):
    __tablename__ = 'specimen'
    specimen_id = db.Column(db.String(), primary_key=True)
    biosample_accession = db.Column(db.String(), nullable=False)
