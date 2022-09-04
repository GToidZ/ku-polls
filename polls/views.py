from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from .models import Question, Choice


def index(request):
    """View for list of recent questions."""
    latest_questions = Question.objects.order_by("-publish_date")[:5]
    ctx = {"latest_questions": latest_questions}
    return render(request, "polls/index.html", ctx)


def details(request, question_id):
    """View for viewing question and its choices."""
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, "polls/details.html", {"question": question})


def vote(request, question_id):
    """View for casting a vote.
    What I learned here: view acts like a path on website, you could also
    use HTTP methods here without showing anything.
    """
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/details.html",
            {"question": question, "error_message": "You didn't choose a choice..."},
        )
    else:
        selected_choice.vote_count += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))


def results(request, question_id):
    """View for seeing results of a poll."""
    try:
        question = Question.objects.get(pk=question_id)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, "polls/results.html", {"question": question})
