"""Tests for Details view"""
from django.test import TestCase, Client
from django.urls import reverse
from polls.tests.utils import (
    new_question_with_relative_date,
    new_choice,
    new_test_user,
    vote,
)


def generate_radio_btn(cid, value, checked: bool = False):
    if checked:
        return f'<input type="radio" checked="true" name="choice" id="choice{cid}" value="{value}">'
    return (
        f'<input type="radio" name="choice" id="choice{cid}" value="{value}">'
    )


class TestDetailsView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = new_test_user("test")
        self.user.set_password("1234")
        self.user.save()

    def test_question_with_choices(self):
        """Published questions have choices displayed"""
        question = new_question_with_relative_date("Test Question")
        choice = new_choice(question, "An ambiguous choice")

        url = reverse("polls:details", args=(question.id,))
        resp = self.client.get(url)

        self.assertContains(
            resp, question.question_text
        )  # Checks if question is displayed
        self.assertContains(resp, choice.choice_text)
        # Checks if choice is displayed

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

    def test_choice_is_selected_after_revisit(self):
        """Choice should be selected when revisiting voted poll"""
        question = new_question_with_relative_date("")
        choice = new_choice(question, "1")
        question.save()

        logged_in = self.client.login(
            username=self.user.username, password="1234"
        )
        self.assertTrue(logged_in)  # Checks for authorization

        url = reverse("polls:details", args=(question.id,))

        # Before voting, should see no choice selected...
        resp = self.client.get(url)
        self.assertContains(resp, generate_radio_btn(choice.id, "1"))

        data = vote(choice, self.user)
        data.save()

        # After voting, should have a choice selected.
        resp = self.client.get(url)
        self.assertContains(resp, generate_radio_btn(choice.id, "1", True))
