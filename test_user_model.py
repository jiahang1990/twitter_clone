"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
        
    def test_user_model(self):
        """Does basic model work?"""

        u1 = User(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD1"
        )

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)
        self.assertEqual(len(u1.following), 0)
        self.assertFalse(u1.is_followed_by(u2))
        self.assertFalse(u2.is_following(u1))

        u1.followers = [u2]
        db.session.commit()

        # User1 should have no messages & 1 followers
        # User2 should have no messages & 1 following
        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 1)
        self.assertEqual(len(u1.following), 0)
        self.assertEqual(len(u2.messages), 0)
        self.assertEqual(len(u2.followers), 0)
        self.assertEqual(len(u2.following), 1)

        self.assertEqual(f"{u1}", f"<User #{u1.id}: {u1.username}, {u1.email}>")
        self.assertTrue(u1.is_followed_by(u2))
        self.assertTrue(u2.is_following(u1))

        u3 = User.signup("testuser3", "test3@test.com", "Password3", "https://cdn.jpegmini.com/user/images/slider_puffin_before_mobile.jpg")
        db.session.commit()
        self.assertEqual(User.query.filter_by(username = "testuser3").first(), u3)
        self.assertTrue(u3.password.startswith("$2b$"))


    def test_invalid_username_signup(self):
        invalid = User.signup(None, "test@test.com", "password", None)
        uid = 1234
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        invalid = User.signup("testtest", None, "password", None)
        uid = 1234
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", "", None)
        
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", None, None)
    