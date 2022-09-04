from django.db import models


class Question(models.Model):
    question_text = models.CharField(max_length=280)
    publish_date = models.DateTimeField("date published")


class Choice(models.Model):
    # Designed with backtracking relationship
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=80)
    vote_count = models.IntegerField(default=0)
