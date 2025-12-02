import os
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vulnsite.settings")
django.setup()

from django.contrib.auth.models import User
from core.models import Profile, Note

def create_user_with_profile(username, email, password, secret_info=""):
    # Create user
    user, created = User.objects.get_or_create(username=username, defaults={"email": email})
    if created:
        user.set_password(password)
        user.save()
        print(f"[+] Created user: {username}")
    else:
        print(f"[i] User already exists: {username}")

    # Create or get Profile
    profile, p_created = Profile.objects.get_or_create(user_id=user.id)
    if p_created or not profile.secret_info:
        profile.secret_info = secret_info
        profile.save()
        print(f"[+] Profile created/updated for: {username}")
    return user


def create_note(user, title, plaintext):
    note = Note.objects.create(user=user, title=title, secret_data=plaintext)
    print(f"[+] Note created for {user.username}: {title}")
    return note


def main():
    print("=== Creating sample users and data ===")

    # Sample users
    alice = create_user_with_profile(
        username="alice",
        email="alice@example.com",
        password="password123",
        secret_info="Alice secret info"
    )

    bob = create_user_with_profile(
        username="bob",
        email="bob@example.com",
        password="password123",
        secret_info="Bob secret info"
    )

    # Sample notes
    create_note(alice, "Alice private note #1", "Alice secret note content")
    create_note(alice, "Alice private note #2", "Alice secret note content 2")
    create_note(bob, "Bob confidential note ✔", "Bob secret note content")

    print("\n=== Sample data creation complete! ===")

if __name__ == "__main__":
    main()