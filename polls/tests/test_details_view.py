import datetime, zoneinfo
from unittest.mock import patch
from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse
from polls.models import Question
from polls.tests.utils import (
    new_question,
    new_question_with_relative_date,
    new_choice,
    new_test_user,
    vote,
)


class TestDetailsView(TestCase):
    def setUp(self):
        client = Client()
        self.user = new_test_user("test")

    def test_question_with_choices(self):
        """Published questions have choices displayed"""
        question = new_question_with_relative_date("Test Question")
        choice = new_choice(question, "An ambiguous choice")

        url = reverse("polls:details", args=(question.id,))
        resp = self.client.get(url)

        self.assertContains(
            resp, question.question_text
        )  # Checks if question is displayed
        self.assertContains(resp, choice.choice_text)  # Checks if choice is displayed

    def test_future_question_should_return_404(self):
        """Unpublished questions return 404 for unauthorized users"""
        question = new_question_with_relative_date("", 1)

        url = reverse("polls:details", args=(question.id,))
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 404)  # Checks if it is 404

    def test_ended_polls_should_redirect(self):
        """Ended questions redirect users to results view"""
        question = new_question_with_relative_date("", -1, -1)

        url = reverse("polls:details", args=(question.id,))
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 302)  # Checks if it is redirected
        self.assertIn(
            ("Location", "/polls/1/results/"), resp.items()
        )  # Checks if the redirect URL is correct
