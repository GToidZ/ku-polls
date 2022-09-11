import datetime, zoneinfo
from unittest.mock import patch
from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse
from .models import Question, Choice


def new_question(question_text, publish_date):
    """Create a Question with question_text and publish_date"""
    return Question.objects.create(
        question_text=question_text, publish_date=publish_date
    )


def new_question_with_relative_date(question_text, days=0, ends=None):
    """
    Create a Question with question_text, publish_date and end_date
    is relative with day count
    """
    at = timezone.now() + datetime.timedelta(days=days)
    question = new_question(question_text, at)
    if ends:
        question.end_date = timezone.now() + datetime.timedelta(days=ends)
    return question


def new_choice(question: Question, choice_text):
    """Create a new Choice for a Question instance"""
    return question.choice_set.create(choice_text=choice_text)


def get_placeholder_time():
    return timezone.datetime(2022, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc)


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

    def test_is_question_published(self):
        """
        is_published() should return True if current date is after publish_date,
        False if not
        """

        question = new_question_with_relative_date("")
        self.assertTrue(question.is_published())

        question = new_question_with_relative_date("", -1)
        self.assertTrue(question.is_published())

        question = new_question_with_relative_date("", 1)
        self.assertFalse(question.is_published())

    @patch("django.utils.timezone.now", new=get_placeholder_time)
    def test_can_vote_on_publish_time(self):
        """
        If current time is equal to published date, can_vote() returns True
        """
        time = get_placeholder_time()
        question = new_question("", time)
        self.assertTrue(question.can_vote())

    @patch("django.utils.timezone.now", new=get_placeholder_time)
    def test_can_vote_on_end_time(self):
        """
        If current time is equal to end date, can_vote() returns True
        """
        time = get_placeholder_time()
        question = new_question("", time - datetime.timedelta(days=1))
        question.end_date = time
        self.assertTrue(question.can_vote())

    def test_cannot_vote_ended_polls(self):
        """
        can_vote() should return False if the poll has already ended
        """
        question = new_question_with_relative_date("", -1, -1)
        self.assertFalse(question.can_vote())


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


class TestIndexView(TestCase):
    client = Client()

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


class TestDetailsView(TestCase):
    client = Client()

    def test_question_with_choices(self):
        """Published questions should have choices displayed"""
        question = new_question_with_relative_date("Test Question")
        choice = new_choice(question, "An ambiguous choice")
        url = reverse("polls:details", args=(question.id,))
        resp = self.client.get(url)
        self.assertContains(resp, question.question_text)
        self.assertContains(resp, choice.choice_text)

    def test_future_question_should_return_404(self):
        """Unpublished questions should return 404 for unauthorized users"""
        question = new_question_with_relative_date("", 1)
        url = reverse("polls:details", args=(question.id,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)


class TestResultsView(TestCase):
    client = Client()

    def test_correct_vote_count_display(self):
        question = new_question_with_relative_date("Test Question")
        new_choice(question, "An ambiguous choice")
        choice = question.choice_set.get(pk=1)
        choice.vote_count += 1
        choice.save()
        url = reverse("polls:results", args=(question.id,))
        resp = self.client.get(url)
        self.assertContains(resp, f"{choice.choice_text}")
        self.assertContains(resp, f'<span class="votes">1</span>')

    def test_future_question_should_return_404(self):
        """Unpublished questions should return 404 for unauthorized users"""
        question = new_question_with_relative_date("", 1)
        url = reverse("polls:results", args=(question.id,))
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)
