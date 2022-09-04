import datetime
from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse
from .models import Question, Choice


def new_question(question_text, publish_date):
    """Create a Question with question_text and publish_date"""
    return Question.objects.create(
        question_text=question_text, publish_date=publish_date
    )


def new_question_with_relative_date(question_text, days=0):
    """
    Create a Question with question_text and publish_date
    is relative with day count
    """
    at = timezone.now() + datetime.timedelta(days=days)
    return new_question(question_text, at)


def new_choice(question: Question, choice_text):
    """Create a new Choice for a Question instance"""
    return question.choice_set.create(choice_text=choice_text)


class TestQuestionModel(TestCase):
    def test_was_published_recently_with_future_instance(self):
        """
        was_published_recently() will return False if
        the question is not yet published
        """

        question = new_question_with_relative_date("", 1)
        self.assertFalse(question.was_published_recently())

    def test_was_published_recently_with_old_instance(self):
        """
        was_published_recently() will return False if
        the question is older than 3 days
        """

        question = new_question_with_relative_date("", -4)
        self.assertFalse(question.was_published_recently())

    def test_choice_list_is_correctly_set(self):
        """
        When creating new Choice(s) in Question they should
        be added to QuerySet
        """

        question = new_question("", timezone.now())
        choice_set_size = question.choice_set.all
        self.assertEqual(0, len(choice_set_size()))

        earliest_choice = new_choice(question, "A")
        new_choice(question, "B")
        latest_choice = new_choice(question, "C")

        self.assertEqual(3, len(choice_set_size()))
        self.assertEqual(earliest_choice, question.choice_set.first())
        self.assertEqual(latest_choice, question.choice_set.last())


class TestChoiceModel(TestCase):
    def test_choice_assigned_to_correct_question(self):
        """When a choice is created, it should be only in one Question"""
        correct_question = new_question("", timezone.now())
        wrong_question = new_question("", timezone.now())

        choice = new_choice(correct_question, "Test")

        self.assertTrue(choice in correct_question.choice_set.all())
        self.assertFalse(choice in wrong_question.choice_set.all())

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
                self.assertEqual(choice.vote_count, count)

        check_votes(0, 0, 0)

        choice = question.choice_set.get(pk=1)
        choice.vote_count += 1
        choice.save()

        check_votes(1, 0, 0)

        choice = question.choice_set.get(pk=2)
        choice.vote_count += 99
        choice.save()

        check_votes(1, 99, 0)
