from django.shortcuts import render, redirect
from django.http import Http404
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.core import exceptions
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Question, Choice, VoteData


def get_published():
    """Returns all questions id that are published"""
    questions = Question.objects.all()
    return [q.id for q in questions if q.is_published()]


@login_required
def vote(request, question_id):
    """
    View for casting a vote. Requires user to be authorized before
    casting their vote. (Accessing this view)

    Namespace: polls:vote

    :param question_id: primary key id of question

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
        user = request.user
        try:
            data = VoteData.objects.get(user=user, choice__in=question.choice_set.all())
        except VoteData.DoesNotExist:
            data = VoteData.objects.create(choice=selected_choice, user=user)
            data.save()
        else:
            data.choice = selected_choice
            data.save()
        return redirect("polls:results", pk=question_id)


class IndexView(generic.ListView):
    """
    View for list of recent questions.

    Namespace: polls:index
    """

    template_name = "polls/index.html"
    context_object_name = "latest_questions"

    def get_queryset(self):
        return Question.objects.filter(id__in=get_published()).order_by("-publish_date")


class DetailsView(generic.DetailView):
    """
    View for viewing question and its choices.

    Namespace: polls:details
    """

    model = Question
    template_name = "polls/details.html"

    def dispatch(self, request, *args, **kwargs):
        self.question_id = kwargs["pk"]
        question = Question.objects.get(pk=self.question_id)
        if not question.is_published():
            raise Http404("Question is unpublished")
        if not question.can_vote():
            return redirect("polls:results", pk=self.question_id)
        return super(DetailsView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        question = Question.objects.get(pk=self.question_id)
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            try:
                selected_choice = VoteData.objects.get(
                    user=user, choice__in=question.choice_set.all()
                ).choice.choice_text
                context["selected_choice"] = selected_choice
            except VoteData.DoesNotExist:
                pass  # Do nothing here, selected_choice is not set
        return context

    def get_queryset(self):
        return Question.objects.filter(id__in=get_published())


class ResultsView(generic.DetailView):
    """
    View for seeing results of a poll.

    Namespace: polls:results
    """

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
