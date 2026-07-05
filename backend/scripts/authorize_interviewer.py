#!/usr/bin/env python3
"""
One-time, interactive OAuth authorization for an interviewer's Google account.

Run this once per interviewer email BEFORE the demo (from the backend/ directory):

    python scripts/authorize_interviewer.py alice.interviewer@gmail.com

It reuses the existing backend/credentials.json OAuth client and opens a browser
consent flow (GoogleCalendarService._start_oauth_flow -> InstalledAppFlow.run_local_server).
The resulting token is saved under backend/tokens/, keyed by a hash of the email,
so the interviewer_calendar_registry can later authenticate as this account non-interactively.
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.calendar_service import GoogleCalendarService


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/authorize_interviewer.py <interviewer_email>")
        sys.exit(1)

    email = sys.argv[1]
    print(f"Starting OAuth flow for {email} ...")
    print("A browser window should open — sign in as this interviewer and grant calendar access.")

    service = GoogleCalendarService()
    ok = service.authenticate(email, force_reauth=True)

    if ok:
        print(f"✅ Authorized {email} — token saved, ready for scheduling.")
    else:
        print(f"❌ Authorization failed for {email}. Check backend/credentials.json and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
