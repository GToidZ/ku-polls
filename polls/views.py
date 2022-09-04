from django.shortcuts import render
from .models import Question


def index(request):
    """View for list of recent questions."""
    latest_questions = Question.objects.order_by("-publish_date")[:5]
    ctx = {"latest_questions": latest_questions}
    return render(request, "polls/index.html", ctx)
