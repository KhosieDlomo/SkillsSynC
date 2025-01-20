# SkillsSynC

### SkillSync Project Instructions

  

---

  

## Project Overview

  

SkillSync is a Python-based Command-Line Interface (CLI) application for managing workshop bookings and one-on-one meetings. The system uses Firebase for authentication and database management and integrates the Google Calendar API for scheduling. It

enables users to:

1. Request meetings with mentors from a database.
2. Schedule one-on-one sessions with peers.
3. Ensure all bookings occur strictly during weekdays (Monday to Friday) between 07:00 and 17:00.

  
The app will be strictly terminal-based and packaged for distribution using `pyinstaller`.

---
## Features
### 1. Authentication

- **Purpose**: Secure user access.
- **Implementation**: Use Firebase Authentication for login and sign-up functionality.
- **Database Integration:**
	-  Store user details (e.g., name, email, role).
	- Maintain user roles such as `mentor` or `peer`.

### 2. Booking System

- **Mentor Sessions:**
	- Fetch and display a list of available mentors.
	- Request a meeting with selected mentors.
- **Peer Sessions:**
	- Search for peers by availability or expertise.
	- Schedule one-on-one meetings.

### 3. Google Calendar Integration

- **Purpose**: Ensure meeting schedules are visible and manageable.
- **Features**:
	- Create calendar events for confirmed bookings.○
	- Send invites to all participants automatically.
	- Enforce meeting times strictly on weekdays between 07:00 and 17:00.

### 4. CLI Functionality
The application will be developed using the `click` library to ensure a user-friendly terminal
interface. The following menu options will be available:

1. **Login:** Authenticate the user.
2. **View Workshops**: List upcoming workshops and mentors available for booking.
3. **Request Meeting**: Request a mentor or peer session.
4. **View Bookings**: Display a list of all confirmed bookings.
5. **Cancel Booking**: Allow users to cancel an existing booking.

5. Database Structure
- Users:
	- user_id: `{ name, email, role (mentor/peer), expertise }`
- Meetings:
	- `meeting_id: { mentor_id, mentee_id/peer_id, time, status }`
- Workshop Requests:
	- `workshop_id: { requestor_id, topic, date_requested }`

---
## Technical Requirements

### 1. Tools and Frameworks
- **Firebase**: For authentication and database.
- **Google Calendar API**: For scheduling meetings.
- **Python Libraries**:
	- `click`: CLI framework.
	- `firebase-admin`: Firebase integration.
	- `google-api-python-client`: Google Calendar integration.
	- `pyinstaller`: To package the app.

### 2. Meeting Time Constraints

- All meetings must occur strictly during weekdays (Monday to Friday) and between
07:00 and 17:00.
- Developers must decide how to enforce and represent this scheduling constraint
within the database and codebase.

---
## Stretch Features

- **Notifications**:
	- Email notifications for meeting confirmations and reminders.(SMTPLIB)
- **Feedback System**:
	- Allow users to rate and leave feedback for mentors and peers.
- **Search Filters**:
	- Enable filtering mentors/peers by expertise or availability.
---
## Packaging and Distribution
- Use `pyinstaller` to convert the Python application into an executable file for easy
distribution.

---
## Next Steps
1. **Set up Firebase**:
	- Configure authentication and database.
2. **Integrate Google Calendar API**:
	- Enable event creation and participant management.
3. **Develop the CLI**:
	- Create interactive terminal commands using `click`.
4. **Test and Package**:
	- Validate features and package the app with `pyinstaller`.
---

	