from django.contrib import admin

from .models import Question, Choice


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["question_text"]}),
        ("Visibility", {"fields": ["visibilty"]}),
        ("Date Information", {"fields": ["publish_date", "end_date"]}),
    ]
    inlines = [ChoiceInline]
    list_display = ("question_text", "visibilty", "publish_date", "end_date")


admin.site.register(Question, QuestionAdmin)
