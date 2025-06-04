from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

def top_view(request):
    if request.user.is_authenticated:
        if not getattr(request.user, "family", None):
            return redirect('family_select')  # family未設定 → 認証選択へ
        return redirect('dashboard')  # familyあり → ダッシュボードへ
    return render(request, 'common/top.html')
