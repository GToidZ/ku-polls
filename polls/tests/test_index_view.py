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


class TestIndexView(TestCase):
    def setUp(self):
        client = Client()
        self.user = new_test_user("test")

    def test_no_questions(self):
        """No polls should be available the first time the server is set up"""
        resp = self.client.get(reverse("polls:index"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "No polls are available at this moment.")
        self.assertQuerysetEqual(resp.context["latest_questions"], [])

    def test_future_question(self):
        """Unpublished questions should not appear in the view"""
        question = new_question_with_relative_date("This should not be seen", 1)
        resp = self.client.get(reverse("polls:index"))
        self.assertContains(resp, "No polls are available at this moment.")
        self.assertQuerysetEqual(resp.context["latest_questions"], [])

    def test_multiple_question(self):
        """Test contains past question and a future one, some should be in view"""
        past = new_question_with_relative_date("This should be seen", -1)
        future = new_question_with_relative_date("This should not be seen", 1)
        resp = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(resp.context["latest_questions"], [past])
