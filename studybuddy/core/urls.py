from django.urls import path

from .views import (
    DashboardView,
    AddSubjectView,
    StartSessionView,
    StopSessionView,
    SubjectDetailView,
    DeleteSubjectView,
    RegisterView
)

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('subjects/add/', AddSubjectView.as_view(), name='add_subject'),
    path('subjects/<int:pk>/', SubjectDetailView.as_view(), name='subject_detail'),
    path('subjects/<int:pk>/delete/',DeleteSubjectView.as_view(),name='delete_subject'),
    path('sessions/start/<int:subject_id>/',StartSessionView.as_view(),name='start_session'),
    path('sessions/stop/',StopSessionView.as_view(),name='stop_session'),
    path('register/',RegisterView.as_view(),name='register'),
]
