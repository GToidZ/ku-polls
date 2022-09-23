"""Tests for Results view"""
from django.test import TestCase, Client
from django.urls import reverse
from polls.tests.utils import (
    new_question_with_relative_date,
    new_choice,
    new_test_user,
    vote,
)


class TestResultsView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = new_test_user("test")

    def test_correct_vote_count_display(self):
        """Results view displays number of votes correctly"""
        question = new_question_with_relative_date("Test Question")
        new_choice(question, "An ambiguous choice")
        choice = question.choice_set.get(pk=1)
        data = vote(choice, self.user)
        data.save()

        url = reverse("polls:results", args=(question.id,))
        resp = self.client.get(url)

        self.assertContains(
            resp, f"{choice.choice_text}"
        )  # Checks if the choice is there
        self.assertContains(
            resp, '<span class="votes">1</span>'
        )  # Checks if the vote is correctly counted

    def test_future_question_should_return_404(self):
        """Unpublished questions should return 404 for unauthorized users"""
        question = new_question_with_relative_date("", 1)

        url = reverse("polls:results", args=(question.id,))
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 404)  # Checks if it is 404
