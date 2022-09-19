import datetime, zoneinfo
from unittest.mock import patch
from django.test import TestCase
from django.utils import timezone
from polls.models import Question
from polls.tests.utils import new_question, new_question_with_relative_date, new_choice


def get_placeholder_time():
    return timezone.datetime(2022, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)


class TestQuestionModel(TestCase):
    def test_was_published_recently_with_future_instance(self):
        """was_published_recently() returns False if a question is not published"""

        question = new_question_with_relative_date("", 1)
        self.assertFalse(question.was_published_recently())

    def test_was_published_recently_with_old_instance(self):
        """was_published_recently() returns False if a question is older than 3 days"""

        question = new_question_with_relative_date("", -4)
        self.assertFalse(question.was_published_recently())

    def test_choice_list_is_correctly_set(self):
        """When creating new Choice(s) in Question they should be added to choice_set"""

        question = new_question("", timezone.now())
        choice_set_size = question.choice_set.all
        self.assertEqual(0, len(choice_set_size()))  # Is it empty?

        # Easy checking: make three choices and use first() and last()
        earliest_choice = new_choice(question, "A")
        new_choice(question, "B")
        latest_choice = new_choice(question, "C")

        self.assertEqual(3, len(choice_set_size()))
        self.assertEqual(earliest_choice, question.choice_set.first())
        self.assertEqual(latest_choice, question.choice_set.last())

    def test_is_question_published(self):
        """is_published() returns True if current time is after publish_date, otherwise False"""

        question = new_question_with_relative_date("")
        self.assertTrue(question.is_published())

        question = new_question_with_relative_date("", -1)
        self.assertTrue(question.is_published())

        question = new_question_with_relative_date("", 1)
        self.assertFalse(question.is_published())

    # Patch the time function to always return placeholder time
    @patch("django.utils.timezone.now", new=get_placeholder_time)
    def test_can_vote_on_publish_time(self):
        """If current time is equal to published date, can_vote() returns True"""
        time = get_placeholder_time()
        question = new_question("", time)
        self.assertTrue(question.can_vote())

    @patch("django.utils.timezone.now", new=get_placeholder_time)
    def test_can_vote_on_end_time(self):
        """If current time is equal to end date, can_vote() returns True"""
        time = get_placeholder_time()
        question = new_question("", time - datetime.timedelta(days=1))
        question.end_date = time
        self.assertTrue(question.can_vote())

    def test_cannot_vote_unpublished_polls(self):
        """can_vote() returns True if the poll hasn't been published yet"""
        question = new_question_with_relative_date("", 1)
        self.assertFalse(question.can_vote())

    def test_cannot_vote_ended_polls(self):
        """can_vote() returns return False if the poll has already ended"""
        question = new_question_with_relative_date("", -1, -1)
        self.assertFalse(question.can_vote())

    def test_invisible_polls_are_not_votable(self):
        """can_vote() returns False if the poll is invisible"""
        question = new_question_with_relative_date("", 0)
        question.visibilty = False
        question.save()
        self.assertFalse(question.can_vote())
