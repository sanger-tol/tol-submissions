import logging

import connexion
from flask_testing import TestCase
import os

from swagger_server.encoder import JSONEncoder

from swagger_server.model import db, \
    SubmissionsUser, SubmissionsRole, SubmissionsState, \
    SubmissionsManifest, SubmissionsSample, SubmissionsSpecimen, \
    SubmissionsSampleField


class BaseTestCase(TestCase):

    api_key = "AnyThingBecAuseThIsIsATEST123456"
    api_key2 = "AnyThingBecAuseThIsIsATEST567890"
    api_key3 = "AnyThingBecAuseThIsIsATEST24680"

    def setUp(self):
        self.maxDiff = None
        db.create_all()
        self.tearDown()
        self.user1 = SubmissionsUser(user_id=100,
                                     name="test_user_requester",
                                     email="test_user_requester@sanger.ac.uk",
                                     organisation="Sanger Institute",
                                     api_key="AnyThingBecAuseThIsIsATEST123456")
        db.session.add(self.user1)
        self.user2 = SubmissionsUser(user_id=200,
                                     name="test_user_admin",
                                     email="test_user_admin@sanger.ac.uk",
                                     organisation="Sanger Institute",
                                     api_key="AnyThingBecAuseThIsIsATEST567890")
        db.session.add(self.user2)
        self.user3 = SubmissionsUser(user_id=300,
                                     name="test_user_submitter",
                                     email="test_user_submitter@sanger.ac.uk",
                                     organisation="Sanger Institute",
                                     api_key="AnyThingBecAuseThIsIsATEST24680")
        db.session.add(self.user1)
        db.session.add(self.user2)
        db.session.add(self.user3)
        self.role = SubmissionsRole(role="admin")
        self.role.user = self.user2
        db.session.add(self.role)
        self.role = SubmissionsRole(role="submitter")
        self.role.user = self.user3
        db.session.add(self.role)
        db.session.commit()
        db.engine.execute("ALTER SEQUENCE manifest_manifest_id_seq RESTART WITH 1;")
        db.engine.execute("ALTER SEQUENCE sample_sample_id_seq RESTART WITH 1;")

    def tearDown(self):
        db.session.query(SubmissionsSampleField).delete()
        db.session.query(SubmissionsSample).delete()
        db.session.query(SubmissionsSpecimen).delete()
        db.session.query(SubmissionsManifest).delete()
        db.session.query(SubmissionsRole).delete()
        db.session.query(SubmissionsUser).delete()
        db.session.query(SubmissionsState).delete()
        db.session.commit()
        db.session.remove()

    def create_app(self):
        logging.getLogger('connexion.operation').setLevel('ERROR')
        app = connexion.App(__name__, specification_dir='../swagger/')
        app.app.json_encoder = JSONEncoder
        app.add_api('swagger.yaml', pythonic_params=True)
        app.app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DB_URI']
        app.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app.app)
        return app.app
