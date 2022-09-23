"""Utilities for testing"""
import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from polls.models import Question, Choice, VoteData


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
    when = timezone.now() + datetime.timedelta(days=days)
    question = new_question(question_text, when)
    if ends:
        question.end_date = timezone.now() + datetime.timedelta(days=ends)
        question.save()
    return question


def new_choice(question: Question, choice_text):
    """Create a new Choice for a Question instance"""
    return question.choice_set.create(choice_text=choice_text)


def new_test_user(username):
    """Create a new Django User instance"""
    return User.objects.create(username=username)


def vote(choice: Choice, user: User):
    """Create a new VoteData"""
    return VoteData.objects.create(choice=choice, user=user)
