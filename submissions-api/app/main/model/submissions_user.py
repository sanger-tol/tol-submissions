# SPDX-FileCopyrightText: 2021 Genome Research Ltd.
#
# SPDX-License-Identifier: MIT

from .base import Base, db


class SubmissionsUser(Base):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False, unique=True)
    organisation = db.Column(db.String(), nullable=True)
    api_key = db.Column(db.String(), nullable=True, unique=True)
    token = db.Column(db.String(), nullable=True, unique=True)
    roles = db.relationship('SubmissionsRole', lazy=False)

    def to_dict(self):
        return {'name': self.name,
                'email': self.email,
                'organisation': ('' if self.organisation is None else self.organisation),
                'roles': self.roles}
