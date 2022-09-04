from datetime import timedelta
from django.db import models
from django.utils import timezone


class Question(models.Model):
    question_text = models.CharField(max_length=280)
    publish_date = models.DateTimeField("date published")

    def was_published_recently(self):
        return self.publish_date >= timezone.now() - timedelta(days=3)


class Choice(models.Model):
    # Designed with backtracking relationship
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=80)
    vote_count = models.IntegerField(default=0)
