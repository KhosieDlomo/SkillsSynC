# SkillsSync

SkillsSync is a Python-based application designed to facilitate mentorship and peer collaboration. It integrates Firebase for authentication and database management, Google Calendar for scheduling, and SMTP for email notifications.

---

## Installation

1. **Download the `dist.zip` file:**
   - Download the `dist.zip` archive from the provided link.
  ## Download the Application
You can download the pre-built application from [this Google Drive link]: https://drive.google.com/file/d/1hWnW4MBvwGmS7I6Xse_BN6qOtx_5hgOm/view?usp=drive_link

2. **Extract the contents:**
   - Extract the contents of `dist.zip` to a folder on your computer.

3. **Verify the files:**
   - Ensure the following files are present in the same folder as `main.exe`:
     - `.env` (environment variables).
     - `skillssync-f88a7-firebase-adminsdk-u1lm7-2bf0d05d8f.json` (Firebase credentials).
     - `credentials.json` (Google API credentials).
     - `token.json` (Google OAuth token).

---

## Running the Application

1. **Open a terminal or command prompt:**
   - On **Windows**, press `Win + R`, type `cmd`, and press Enter.
   - On **macOS/Linux**, open the Terminal application.

2. **Navigate to the folder:**
   - Use the `cd` command to navigate to the folder where you extracted the `dist.zip` contents. For example:
     ```bash
     cd path\to\extracted\folder
     ```

3. **Run the executable:**
   - On **Windows**, run:
     ```bash
     main.exe
     ```
   - On **macOS/Linux**, run:
     ```bash
     ./main
     ```

---

## Troubleshooting

### **File Not Found Errors**
- Ensure all required files (`.env`, Firebase credentials, etc.) are in the same folder as `main.exe`.

### **Firebase/Google API Errors**
- Verify that the credentials files are correct and not expired.
- Ensure the `.env` file contains valid environment variables.

### **Email Notifications**
- Ensure your email credentials in `.env` are correct.
- Check that your email provider allows SMTP access.

---

## Support

For assistance, please contact khosidlomo012@gmail.com.

---

-----------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------
# SkillsSynC

### SkillSync Project Instructions

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

	