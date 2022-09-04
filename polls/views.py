from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from .models import Question, Choice


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


class IndexView(generic.ListView):
    """View for list of recent questions."""

    template_name = "polls/index.html"
    context_object_name = "latest_questions"

    def get_queryset(self):
        return Question.objects.order_by("-publish_date")[:5]


class DetailsView(generic.DetailView):
    """View for viewing question and its choices."""

    model = Question
    template_name = "polls/details.html"


class ResultsView(generic.DetailView):
    """View for seeing results of a poll."""

    model = Question
    template_name = "polls/results.html"
