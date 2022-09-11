from datetime import timedelta
from django.db import models
from django.utils import timezone


class Question(models.Model):
    """Model for Question with publishing date"""

    question_text = models.CharField(max_length=280)
    publish_date = models.DateTimeField("date published")
    end_date = models.DateTimeField("date closed", default=None, null=True)
    visibilty = models.BooleanField("poll visibility", default=True)

    def is_published(self):
        if not self.visibilty:
            return False
        return timezone.now() >= self.publish_date

    def was_published_recently(self):
        return timezone.now() >= self.publish_date >= timezone.now() - timedelta(days=3)

    def can_vote(self):
        if not end_date:
            return True
        return self.end_date >= timezone.now() >= self.publish_date

    def __str__(self):
        return f"{self.question_text}"


class Choice(models.Model):
    """
    Model for Choice that makes relationship with Question
    and has a counter
    """

    # Designed with backtracking relationship
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=80)
    vote_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.choice_text}; with {self.vote_count} vote(s)"
