"""Tests for VoteData model"""
from django.test import TestCase
from django.utils import timezone
from polls.tests.utils import (
    new_question,
    new_choice,
    new_test_user,
    vote,
)


class TestVoteDataModel(TestCase):
    def setUp(self):
        self.question = new_question("", timezone.now())
        self.choice = new_choice(self.question, "Test")
        self.user = new_test_user("test")

    def test_votedata_model_str(self):
        """Test for __str__ in VoteData"""
        votedata = vote(self.choice, self.user)
        self.assertEqual("test voting for Test", str(votedata))
