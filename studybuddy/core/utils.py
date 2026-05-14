from django.utils import timezone
from datetime import timedelta
from .models import StudySession, Streak


def update_streak(user):
    today = timezone.now().date()

    sessions = StudySession.objects.filter(
        user=user,
        start_time__date=today,
        duration__gte=600
    )

    if not sessions.exists():
        return

    streak, _ = Streak.objects.get_or_create(
        user=user
    )

    if streak.last_activity_date == today:
        return

    yesterday = today - timedelta(days=1)

    if streak.last_activity_date == yesterday:
        streak.current_streak += 1
    else:
        streak.current_streak = 1

    streak.last_activity_date = today

    if streak.current_streak > streak.max_streak:
        streak.max_streak = streak.current_streak

    streak.save()