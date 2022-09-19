import datetime, zoneinfo
from unittest.mock import patch
from django.test import TestCase
from django.utils import timezone
from polls.models import Question
from polls.tests.utils import (
    new_question,
    new_question_with_relative_date,
    new_choice,
    new_test_user,
    vote,
)


class TestChoiceModel(TestCase):
    def setUp(self):
        self.user = new_test_user("test")

    def test_choice_assigned_to_correct_question(self):
        """When a choice is created, it should be only in one Question"""
        correct_question = new_question("", timezone.now())
        wrong_question = new_question("", timezone.now())

        choice = new_choice(correct_question, "Test")

        self.assertTrue(
            choice in correct_question.choice_set.all()
        )  # Checks if the choice is in correct Question
        self.assertFalse(
            choice in wrong_question.choice_set.all()
        )  # Checks if the choice is not in wrong Question

    def test_vote_count_updates(self):
        """When a choice is voted, it should be correctly counted"""
        question = new_question("", timezone.now())
        new_choice(question, "A")
        new_choice(question, "B")
        new_choice(question, "C")

        def check_votes(*counts):
            if len(counts) != len(question.choice_set.all()):
                raise ValueError("Counts are not the same length as choices")
            for choice, count in zip(question.choice_set.all(), counts):
                self.assertEqual(
                    choice.vote_count, count
                )  # Checks for correct vote count of each choice

        check_votes(0, 0, 0)

        choice = question.choice_set.get(pk=1)
        vote(choice, self.user)

        check_votes(1, 0, 0)

        choice = question.choice_set.get(pk=2)
        vote(choice, self.user)

        check_votes(1, 1, 0)
