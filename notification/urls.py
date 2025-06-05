# notification/urls.py

from django.urls import path
from .views import manual_notify_runner

urlpatterns = [
    # ── 既存の URL パターン ──
    # path("run_notifications/", some_other_view, name="run_line_notifications"), 
    # …

    # ここから追加
    path("manual-run/", manual_notify_runner, name="manual_notify_runner"),
]
