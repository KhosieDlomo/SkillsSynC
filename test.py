# import datetime
# import os
# import click
# from firebase_auth import db
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from google.auth.transport.requests import Request
# from googleapiclient.errors import HttpError
# from googleapiclient.discovery import Resource

# SCOPES = [
#     "https://www.googleapis.com/auth/calendar",
#     "https://www.googleapis.com/auth/calendar.events",
# ]


# def get_calendar():
#     cred = None
#     if os.path.exists("token.json"):
#         cred = Credentials.from_authorized_user_file("token.json", SCOPES)

#     if not cred or not cred.valid:
#         if cred and cred.expired and cred.refresh_token:
#             cred.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 "credentials.json", SCOPES
#             )
#             cred = flow.run_local_server(port=0)
#         with open("token.json", "w") as token:
#             token.write(cred.to_json())
#     return build("calendar", "v3", credentials=cred)


# @click.command()
# def bookings():
#     service = get_calendar()

#     subject = input("Event subject: ")
#     date = input("Event date(DD-MM-YYYY): ")
#     start_time = input("Event start time (HH-MM): ")
#     end_time = input("Event end time (HH-MM): ")
#     attendees = input("Emails of the participants: ").split(",")
#     location = input("Event Location (e.g: 'Online' or a physical address): ")

#     start_hour = datetime.datetime.strptime(f"{date} {start_time}", "%d-%m-%Y %H:%M")
#     end_hour = datetime.datetime.strptime(f"{date} {end_time}", "%d-%m-%Y %H:%M")

#     if start_hour.weekday() >= 5 or start_hour.hour < 7 or end_hour.hour > 17:
#         click.echo(
#             "Error! Meetings are only allowed on weekdays between 07:00 to 17:00."
#         )
#         return

#     time_min = start_hour.isoformat() + "Z"
#     time_max = end_hour.isoformat() + "Z"
#     event_result = (
#         service.events()
#         .list(
#             calendarId="primary",
#             timeMin=time_min,
#             timeMax=time_max,
#             singleEvents=True,
#         )
#         .execute()
#     )
#     events = event_result.get("items", [])
#     if events:
#         click.echo("Schedule for another meeting at this time. Select a different time.")
#         return

#     event = {
#         "summary": subject,
#         "location": location,
#         "start": {"dateTime": start_hour.isoformat(), "timeZone": "UTC"},
#         "end": {"dateTime": end_hour.isoformat(), "timeZone": "UTC"},
#         "attendees": [{"email": email.strip()} for email in attendees],
#         "reminders": {
#             "useDefault": False,
#             "overrides": [
#                 {"method": "email", "minutes": 24 * 60},
#                 {"method": "popup", "minutes": 15},
#             ],
#         },
#     }
#     try:
#         event_result = (
#             service.events()
#             .insert(calendarId="primary", body=event, sendUpdates="all")
#             .execute()
#         )
#         db.collection("meetings").add(
#             {
#                 "subject": subject,
#                 "date": date,
#                 "start_time": start_hour.isoformat(),
#                 "end_time": end_hour.isoformat(),
#                 "attendees": attendees,
#                 "location": location,
#                 "status": "confirmed",
#                 "google_event_id": event_result.get("id"),
#             }
#         )
#         click.echo(f"Event created successfully: {event_result.get('htmlLink')}")

#     except HttpError as error:
#         print(f"An error occurred: {error}")


# @click.command()
# def view_booking():
#     """View all your confirmed bookings."""
#     email = input("Enter your email to fetch bookings: ")

#     try:
#         bookings = (
#             db.collection("meetings").where("attendees", "array_contains", email).stream()
#         )
#         click.echo(f"Bookings for {email}:")
#         for booking in bookings:
#             data = booking.to_dict()
#             click.echo(
#                 f"Subject: {data['subject']}, Date: {data['date']}, Time: {data['start_time']} - {data['end_time']}"
#             )
#     except Exception as e:
#         click.echo(f"Error fetching bookings: {e}")


# @click.command()
# def cancel_booking():
#     """Cancel an existing booking."""
#     event_id = input("Enter the event ID to cancel: ")

#     try:
#         # Remove from Google Calendar
#         cred = Credentials.from_authorized_user_file("token.json", SCOPES)
#         service = build("calendar", "v3", credentials=cred)

#         if service:
#             try:
#                 service.events().delete(calendarId="primary", eventId=event_id).execute()
#             except HttpError as e:
#                 click.echo(f"Error deleting from Google Calendar: {e}")
#                 return

#             # Remove from Firestore
#             meetings = (
#                 db.collection("meetings").where("google_event_id", "==", event_id).stream()
#             )
#             deleted = False
#             for meeting in meetings:
#                 db.collection("meetings").document(meeting.id).delete()
#                 deleted = True
#             if not deleted:
#                 click.echo(f"Booking with event id: '{event_id}' not found")
#                 return
#             click.echo("Booking successfully canceled.")
#     except Exception as e:
#         click.echo(f"Error canceling booking: {e}")


# @click.command()
# def view_workshops():
#     """View available workshops and mentors."""
#     try:
#         workshops = db.collection("workshops").stream()
#         click.echo("Available Workshops:")
#         for workshop in workshops:
#             data = workshop.to_dict()
#             click.echo(f"  - Topic: {data['topic']}")
#             click.echo(f"    Mentors:")
#             for mentor_id in data.get("mentors", []):
#                 mentor = db.collection("users").document(mentor_id).get()
#                 if mentor.exists:
#                      mentor_data = mentor.to_dict()
#                      click.echo(f"      - {mentor_data.get('name')} ({mentor_data.get('email')})")
#                 else:
#                      click.echo(f"      - Mentor ID {mentor_id} not found")
#             click.echo("-" * 20)  # Separator
#     except Exception as e:
#         click.echo(f"Error fetching workshops: {e}")


# @click.command()
# def request_meeting():
#     """Request a meeting with a mentor or peer."""
#     role = input("Request a meeting with a (mentor/peer): ").lower()

#     if role not in ["mentor", "peer"]:
#         click.echo("Error: Invalid role. Please enter 'mentor' or 'peer'.")
#         return

#     try:
#          if role == "mentor":
#              users = db.collection('users').where('role', '==', 'mentor').stream()
#          elif role == 'peer':
#             users = db.collection('users').where('role', '==', 'peer').stream()

#          user_list = [user.to_dict() for user in users if user.exists ]
#          if not user_list:
#               click.echo(f'No {role} available')
#               return

#          click.echo(f"Available {role}s:")
#          for i, user in enumerate(user_list):
#             click.echo(f"  {i+1}. {user['name']} ({user['email']})")

#          while True:
#              try:
#                 selection = int(input(f'Enter the number of the {role} to book:'))-1
#                 if 0 <= selection < len(user_list):
#                     selected_user = user_list[selection]
#                     break
#                 else:
#                    click.echo('Error! Invalid selection')
#              except ValueError:
#                  click.echo('Error! please enter a valid number')

#          subject = input("Event subject: ")
#          date = input("Event date(DD-MM-YYYY): ")
#          start_time = input("Event start time (HH-MM): ")
#          end_time = input("Event end time (HH-MM): ")
#          location = input("Event Location (e.g: 'Online' or a physical address): ")

#          start_hour = datetime.datetime.strptime(f"{date} {start_time}", "%d-%m-%Y %H:%M")
#          end_hour = datetime.datetime.strptime(f"{date} {end_time}", "%d-%m-%Y %H:%M")

#          if start_hour.weekday() >= 5 or start_hour.hour < 7 or end_hour.hour > 17:
#              click.echo(
#                  "Error! Meetings are only allowed on weekdays between 07:00 to 17:00."
#              )
#              return

#          time_min = start_hour.isoformat() + "Z"
#          time_max = end_hour.isoformat() + "Z"
#          service = get_calendar()
#          event_result = (
#             service.events()
#             .list(
#                 calendarId="primary",
#                 timeMin=time_min,
#                 timeMax=time_max,
#                 singleEvents=True,
#             )
#             .execute()
#          )
#          events = event_result.get("items", [])
#          if events:
#             click.echo("Schedule for another meeting at this time. select different time.")
#             return

#          event = {
#             "summary": subject,
#             "location": location,
#             "start": {"dateTime": start_hour.isoformat(), "timeZone": "UTC"},
#             "end": {"dateTime": end_hour.isoformat(), "timeZone": "UTC"},
#             "attendees": [{"email": selected_user['email']}],
#             "reminders": {
#                 "useDefault": False,
#                 "overrides": [
#                    {"method": "email", "minutes": 24 * 60},
#                    {"method": "popup", "minutes": 15},
#                    ],
#               },
#           }
#          try:
#                 event_result = (
#                    service.events()
#                    .insert(calendarId="primary", body=event, sendUpdates="all")
#                    .execute()
#                 )
#                 db.collection("meetings").add(
#                    {
#                      "subject": subject,
#                      "date": date,
#                      "start_time": start_hour.isoformat(),
#                      "end_time": end_hour.isoformat(),
#                      "attendees": [selected_user['email']],
#                      "location": location,
#                      "status": "confirmed",
#                      "google_event_id": event_result.get("id"),
#                      "mentor_id": selected_user['email'] if role == "mentor" else None, # Add mentor id to meeting if applicable
#                      "peer_id": selected_user['email'] if role == "peer" else None # Add peer id to meeting if applicable

#                    }
#                  )
#                 click.echo(f"Event created successfully: {event_result.get('htmlLink')}")
#          except HttpError as error:
#              print(f"An error occured: {error}")
#     except Exception as e:
#             click.echo(f'Error requesting meeting {e}')