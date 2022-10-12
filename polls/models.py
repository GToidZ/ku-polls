from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Question(models.Model):
    """
    Model for Question with publishing date

    :param question_text: question's short description
    :param publish_date: datetime when poll should be published
    :param end_date: datetime when poll should ended
    :param visibility: poll is hidden from users or not
    """

    question_text = models.CharField(max_length=280)
    publish_date = models.DateTimeField("date published")
    end_date = models.DateTimeField(
        "date closed", default=None, null=True, blank=True
    )
    visibilty = models.BooleanField("poll visibility", default=True)

    def is_published(self):
        if not self.visibilty:
            return False
        return timezone.now() >= self.publish_date

    def was_published_recently(self):
        return (
            timezone.now()
            >= self.publish_date
            >= timezone.now() - timedelta(days=3)
        )

    def can_vote(self):
        if not self.is_published():
            return False
        if not self.end_date:
            return True
        return self.end_date >= timezone.now() >= self.publish_date

    def __str__(self):
        return f"{self.question_text}"


class Choice(models.Model):
    """
    Model for Choice that makes relationship with Question
    and has a counter

    :param question: what Question does this relevant to
    :param choice_text: choice's short description
    """

    # Designed with backtracking relationship
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=80)

    @property
    def vote_count(self):
        return VoteData.objects.filter(choice=self).count()

    def __str__(self):
        return f"{self.choice_text}; with {self.vote_count} vote(s)"


class VoteData(models.Model):
    """
    Model for a voting data where each vote contains associating user
    and choice that they have voted

    :param user: who voted for the choice
    :param choice: the choice that has been selected
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} voting for {self.choice.choice_text}"
