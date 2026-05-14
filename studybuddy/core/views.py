from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, CreateView, DetailView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .models import Subject, StudySession, Streak
from .utils import update_streak
from django.http import JsonResponse
import json

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'tracker/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = timezone.now().date()

        subjects = Subject.objects.filter(user=self.request.user)

        sessions = StudySession.objects.filter(
            user=self.request.user,
            start_time__date=today
        )

        total_today = sum(session.duration for session in sessions)

        streak, _ = Streak.objects.get_or_create(
            user=self.request.user
        )

        context['subjects'] = subjects
        context['sessions'] = sessions
        context['total_today'] = total_today
        context['streak'] = streak
        context['chart_labels'] = json.dumps([
            s.subject.name for s in sessions
        ])

        context['chart_data'] = json.dumps([
            s.duration for s in sessions
        ])
        return context

class AddSubjectView(LoginRequiredMixin, CreateView):
    model = Subject
    template_name = 'tracker/add_subject.html'
    fields = ['name']
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class StartSessionView(View):

    def post(self, request, subject_id):

        subject = get_object_or_404(
            Subject,
            id=subject_id,
            user=request.user
        )

        StudySession.objects.filter(
            user=request.user,
            end_time__isnull=True
        ).update(
            end_time=timezone.now()
        )

        session = StudySession.objects.create(
            user=request.user,
            subject=subject,
            start_time=timezone.now()
        )

        return JsonResponse({
            "success": True,
            "session_id": session.id,
            "start_time": session.start_time.timestamp(),
            "subject": subject.name
        })

from django.views import View
from django.http import JsonResponse
from django.utils import timezone

from .models import StudySession
from .utils import update_streak


class StopSessionView(View):
    def post(self, request):
        session = StudySession.objects.filter(
            user=request.user,
            end_time__isnull=True
        ).first()

        if not session:
            return JsonResponse({
                "success": False,
                "message": "No active session"
            })

        session.end_time = timezone.now()

        duration = (
            session.end_time - session.start_time
        ).total_seconds()

        session.duration = int(duration)
        session.save()
        update_streak(request.user)

        return JsonResponse({
            "success": True,
            "duration": session.duration,
            "message": "Session stopped"
        })

class SubjectDetailView(LoginRequiredMixin, DetailView):
    model = Subject
    template_name = 'tracker/subject_detail.html'
    context_object_name = 'subject'

    def get_queryset(self):
        return Subject.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        sessions = StudySession.objects.filter(
            subject=self.object
        )

        total_time = sum(
            session.duration for session in sessions
        )

        context['sessions'] = sessions
        context['total_time'] = total_time

        return context

from django.views.generic import DeleteView

class DeleteSubjectView(LoginRequiredMixin, DeleteView):
    model = Subject
    success_url = reverse_lazy('dashboard')

    def get_queryset(self):
        return Subject.objects.filter(user=self.request.user)

from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.models import User
from .forms import RegisterForm

class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')