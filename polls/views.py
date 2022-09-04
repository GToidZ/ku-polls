from django.shortcuts import render
from django.http import Http404
from .models import Question


def index(request):
    """View for list of recent questions."""
    latest_questions = Question.objects.order_by("-publish_date")[:5]
    ctx = {"latest_questions": latest_questions}
    return render(request, "polls/index.html", ctx)


def details(request, question_id):
    """View for viewing question, choices and results; and for casting votes."""
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, "polls/details.html", {"question": question})
