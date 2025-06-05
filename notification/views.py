# notification/views.py

from django.http import JsonResponse
from django.views.decorators.http import require_GET

# 事前に用意しているスクリプトを呼び出す
# ※ scripts/notify_runner.py 内に定義されている関数を使う
from scripts.notify_runner import run_line_notifications

@require_GET
def manual_notify_runner(request):
    """
    UptimeRobot など外部サービスからの GET リクエストで通知処理を実行するエンドポイント。
    - run_line_notifications() を呼び出し、結果を JSON で返す。
    - もし例外が発生すれば 500 ステータスでエラー内容を返す。
    """
    try:
        run_line_notifications()
        return JsonResponse({"status": "ok", "message": "通知処理を実行しました"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
