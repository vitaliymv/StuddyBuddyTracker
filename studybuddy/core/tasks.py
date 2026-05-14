from celery import shared_task
from django.contrib.auth.models import User
from datetime import date, timedelta

from .models import StudySession, Streak


@shared_task
def check_streaks():
    today = date.today()
    yesterday = today - timedelta(days=1)

    users = User.objects.all()

    for user in users:
        streak, created = Streak.objects.get_or_create(user=user)

        # 🔍 перевіряємо чи була валідна сесія
        has_valid_session = StudySession.objects.filter(
            user=user,
            duration__gte=600,  # 10 хв
            start_time__date=yesterday
        ).exists()

        if has_valid_session:
            # якщо вчора був активний → продовжуємо streak
            if streak.last_activity_date == yesterday:
                streak.current_streak += 1
            else:
                streak.current_streak = 1

            streak.last_activity_date = yesterday

            if streak.current_streak > streak.max_streak:
                streak.max_streak = streak.current_streak

        else:
            # ❌ streak падає
            streak.current_streak = 0

        streak.save()