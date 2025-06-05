# （修正後）notification/views.py

from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt

from scripts.notify_runner import run_line_notifications

@csrf_exempt
def manual_notify_runner(request):
    """
    GET および HEAD リクエストを許可し、notify_runner を実行します。
    HEAD リクエストの場合もステータスだけ 200 で返します。
    """
    # HEAD または GET のみを許可
    if request.method not in ("GET", "HEAD"):
        return HttpResponseNotAllowed(permitted_methods=["GET", "HEAD"])

    try:
        # HEAD の場合も run_line_notifications() を実行してよいなら以下のまま実行
        # もし HEAD で実行したくなければ、request.method == "GET" のみ実行するよう分岐してもよい
        run_line_notifications()
        # GET/HEAD に対してステータス 200 を返す
        return JsonResponse({"status": "ok", "message": "通知処理を実行しました"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
