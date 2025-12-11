from django.shortcuts import render, HttpResponse
from django.db import connection
from urllib.parse import urlparse
import requests
import html

from .models import Profile

def home(request):
    return render(request, "core/home.html")

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('/')

# FLAW 1: Broken Access Control (A01)
# Any user can view any profile

def profile_detail(request, user_id):
    profile = Profile.objects.get(id=user_id) # No permission check
    return render(request, "core/profile.html", {"profile": profile})


# Fix: require user to login
# You can see the usernames and passwords in vulnsite/sample_data.py

# from django.http import HttpResponseForbidden
# from django.contrib.auth.decorators import login_required

# @login_required
# def profile_detail(request, user_id):
#     profile = Profile.objects.filter(id=user_id).first()
#     if not profile:
#         return HttpResponse('Not found', status=404)
#     if profile.user_id != request.user.id and not request.user.is_staff:
#         return HttpResponseForbidden('Forbidden')
#     return render(request, 'core/profile.html', {'profile': profile})


# FLAW 2: SQL Injection (A03)
# raw SQL built with string concat

def search_users(request):
    q = request.GET.get('q', '')
    # Vulnerable raw SQL string concatenation
    raw = f"""
    SELECT p.id, u.username, p.secret_info
    FROM core_profile p
    JOIN auth_user u ON p.user_id = u.id
    WHERE u.username LIKE '%{q}%';
    """
    with connection.cursor() as cursor:
        cursor.execute(raw)
        rows = cursor.fetchall()
    return render(request, 'core/search.html', {'rows': rows, 'query': q})

# Fix: parameterized query or ORM
# def search_users(request):
#     q = request.GET.get('q', '')
#     raw = """
#     SELECT p.id, u.username, p.secret_info
#     FROM core_profile p
#     JOIN auth_user u ON p.user_id = u.id
#     WHERE u.username LIKE %s;
#     """
#     with connection.cursor() as cursor:
#         cursor.execute(raw, [f"%{q}%"])
#         rows = cursor.fetchall()
#     return render(request, 'core/search.html', {'rows': rows, 'query': q})


# FLAW 3: Reflected XSS (A07)
# user input rendered unsafely

def xss_demo(request):
    comment = request.GET.get("comment", "")
    return render(request, "core/xss.html", {"comment": comment}) # Input rendered without escaping

# Fix: don't mark untrusted input as safe
# def xss_demo(request):
#     comment = request.GET.get("comment", "")
#     safe_comment = html.escape(comment)
#     return render(request, "core/xss.html", {"comment": safe_comment})

# FLAW 4: SSRF (A10)
def fetch_url(request):
    url = request.GET.get('url')
    if not url:
        return HttpResponse('Provide ?url=...')
    resp = requests.get(url) # Fetches any url given
    return HttpResponse(resp.text[:1000])

# Fix: validate host and scheme
# ALLOWED = ['example.com']
# def fetch_url(request):
#     url = request.GET.get('url')
#     parsed = urlparse(url)
#     if parsed.scheme not in ('http', 'https'):
#         return HttpResponse('Invalid scheme', status=400)
#     if parsed.hostname not in ALLOWED:
#         return HttpResponse('Blocked', status=403)
#     resp = requests.get(url)
#     return HttpResponse(resp.text[:1000])

# FLAW 5: Security Misconfiguration (A05)
# Can access debug information
from django.conf import settings

def debug_info(request):
    """
    VULNERABLE: Exposes sensitive configuration settings if DEBUG=True.
    Demonstrates Security Misconfiguration (A05).
    """
    if settings.DEBUG:
        # Show sensitive info (DEMO ONLY)
        return HttpResponse(f"""
            <h1>DEBUG INFO LEAK</h1>
            <p><b>Debug:</b> {settings.DEBUG}</p>
            <p><b>Installed Apps:</b> {settings.INSTALLED_APPS}</p>
            <p><b>Middleware:</b> {settings.MIDDLEWARE}</p>
        """)

    return HttpResponse("Debug mode disabled")

# Fix: prevent debug info from being available
# This can be fixed by setting DEBUG = False in the settings in vulnsite/settings.py
