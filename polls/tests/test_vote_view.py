"""Tests for vote() view"""
from django.test import TestCase, Client
from django.urls import reverse
from polls.models import VoteData
from polls.tests.utils import (
    new_question_with_relative_date,
    new_choice,
    new_test_user,
)


def post_with(i):
    return {"choice": i}  # For creating POST data


class TestVoteView(TestCase):
    """
    Tests for the vote() view; containing,

    * Checks if the view redirects whenever the user is not authorized.
    * Checks if VoteData is changed when the same user voted
      for the same question again.
    """

    def setUp(self):
        self.client = Client()
        self.user = new_test_user("test")
        self.user.set_password("1234")
        self.user.save()

    def test_vote_view_redirect_when_not_logged_in(self):
        """Users that are not logged in gets redirected to login page"""
        question = new_question_with_relative_date("")
        choice = new_choice(question, "")
        question.save()

        url = reverse("polls:vote", args=(question.id,))
        data = {"choice": choice.id}
        resp = self.client.post(url, data)

        self.assertEqual(resp.status_code, 302)  # Checks if it is redirected
        self.assertIn(
            ("Location", f"/accounts/login/?next=/polls/{question.id}/vote/"),
            resp.items(),
        )  # Checks if the redirect URL is correct

    def test_vote_view_user_changes_their_vote(self):
        """
        Users can change their vote,
        the VoteData object changes but should not be recreated in database
        """
        logged_in = self.client.login(
            username=self.user.username, password="1234"
        )
        self.assertTrue(logged_in)  # Checks for authorization

        question = new_question_with_relative_date("")
        choice1 = new_choice(question, "A")
        choice2 = new_choice(question, "B")
        question.save()

        url = reverse("polls:vote", args=(question.id,))

        def fetch_vote():
            # For fetching VoteData associated with user
            return VoteData.objects.filter(
                user=self.user, choice__in=question.choice_set.all()
            )

        self.client.post(url, post_with(choice1.id))
        self.assertEqual(fetch_vote().count(), 1)
        self.assertEqual(fetch_vote().first().choice, choice1)

        self.client.post(url, post_with(choice2.id))
        self.assertEqual(
            fetch_vote().count(), 1
        )  # Checks that VoteData is not recreated
        self.assertEqual(
            fetch_vote().first().choice, choice2
        )  # Checks if VoteData is changed

    def test_question_does_not_exist_for_voting(self):
        """When trying to vote for non-existant question, it should return 404"""
        logged_in = self.client.login(
            username=self.user.username, password="1234"
        )
        self.assertTrue(logged_in)  # Checks for authorization

        url = reverse("polls:vote", args=(9999,))
        resp = self.client.post(url, post_with(9999))

        self.assertEqual(resp.status_code, 404)

    def test_choice_does_not_exist_for_voting(self):
        """When trying to vote for non-existant choice, it should show an error message"""
        logged_in = self.client.login(
            username=self.user.username, password="1234"
        )
        self.assertTrue(logged_in)  # Checks for authorization

        question = new_question_with_relative_date("")
        new_choice(question, "A")
        question.save()

        url = reverse("polls:vote", args=(question.id,))
        resp = self.client.post(url, post_with(9999))

        # Use &#x27; for substituting single-quote character.
        self.assertContains(resp, "You didn&#x27;t choose a choice!")
