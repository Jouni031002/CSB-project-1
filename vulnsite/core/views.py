from django.shortcuts import render, HttpResponse
from django.db import connection
from urllib.parse import urlparse
import requests
import html

from .models import Profile

def home(request):
    return render(request, "core/home.html")

# FLAW 1: Broken Access Control (A01)
# Any user can view any profile

def profile_detail(request, user_id):
    profile = Profile.objects.get(id=user_id) # No permission check
    return render(request, "core/profile.html", {"profile": profile})


# Fix: require user to be owner or staff
# from django.http import HttpResponseForbidden
# def profile_detail(request, user_id):
#     if not request.user.is_authenticated:
#         return HttpResponseForbidden('Login required')
#     if profile := Profile.objects.filter(id=user_id).first():
#         if profile.user != request.user and not request.user.is_staff:
#             return HttpResponseForbidden('Forbidden')
#         return render(request, 'core/profile.html', {'profile': profile})
#     return HttpResponse('Not found', status=404)

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
# def search_users_safe(request):
#     q = request.GET.get('q', '')
#     # raw = """
    # SELECT p.id, u.username, p.secret_info
    # FROM core_profile p
    # JOIN auth_user u ON p.user_id = u.id
    # WHERE u.username LIKE %s;
    # """
    # with connection.cursor() as cursor:
    #     cursor.execute(raw, [f"%{q}%"])
    #     rows = cursor.fetchall()
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

# FLAW 4: Insecure Direct Object Reference (IDOR) (A01)

def idor_profile(request, profile_id):
    profile = Profile.objects.get(id=profile_id)
    return HttpResponse(f"Private info: {profile.secret_info}") # No access control

# Fix: check permissions
# from django.http import HttpResponseForbidden
# def idor_profile(request, profile_id):
#     profile = Profile.objects.get(id=profile_id)
#     if not request.user.is_authenticated or profile.user != request.user:
#         return HttpResponseForbidden('Forbidden')
#     return HttpResponse(f'Private info: {profile.secret_info}')

# FLAW 5: SSRF (A10)
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

# FLAW 6: Cryptographic Failure (A02)
# Sensitive data stored and displayed in plaintext

from .models import Profile, Note

def show_note(request, note_id):
    note = Note.objects.get(id=note_id)
    return HttpResponse(f"Note: {note.title}<br>Secret: {note.secret_data}") # Unencrypted, revealed in plaintext.

# Fix: encrypt sensitive data and require authentication

# from django.contrib.auth.decorators import login_required
# from cryptography.fernet import Fernet

# cipher_key = Fernet.generate_key()
# cipher = Fernet(cipher_key)

# @login_required
# def show_note(request, note_id):
#     note = Note.objects.get(id=note_id)
#     decrypted = cipher.decrypt(note.secret_data.encode()).decode()
#     return HttpResponse(f"Note: {note.title}<br>Secret: {decrypted}")