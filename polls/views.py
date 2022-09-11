from django.shortcuts import render, redirect
from django.http import Http404
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from .models import Question, Choice


def get_published():
    questions = Question.objects.all()
    return [q.id for q in questions if q.is_published()]


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
        messages.error(request, "You didn't choose a choice!")
        return render(
            request,
            "polls/details.html",
            {"question": question},
        )
    else:
        selected_choice.vote_count += 1
        selected_choice.save()
        return redirect("polls:results", pk=question_id)


class IndexView(generic.ListView):
    """View for list of recent questions."""

    template_name = "polls/index.html"
    context_object_name = "latest_questions"

    def get_queryset(self):
        return Question.objects.filter(id__in=get_published()).order_by("-publish_date")


class DetailsView(generic.DetailView):
    """View for viewing question and its choices."""

    model = Question
    template_name = "polls/details.html"

    def dispatch(self, request, *args, **kwargs):
        question_id = kwargs["pk"]
        if not Question.objects.get(pk=question_id).can_vote():
            return redirect("polls:results", pk=question_id)
        return super(DetailsView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Question.objects.filter(id__in=get_published())


class ResultsView(generic.DetailView):
    """View for seeing results of a poll."""

    model = Question
    template_name = "polls/results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_votes"] = sum(
            [c.vote_count for c in context["question"].choice_set.all()]
        )
        return context

    def get_queryset(self):
        return Question.objects.filter(id__in=get_published())
