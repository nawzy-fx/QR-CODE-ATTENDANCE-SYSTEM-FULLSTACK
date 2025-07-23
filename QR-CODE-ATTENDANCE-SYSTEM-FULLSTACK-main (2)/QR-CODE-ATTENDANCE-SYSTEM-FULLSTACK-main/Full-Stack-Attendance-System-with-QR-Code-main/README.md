# Full-Stack Attendance System with QR Code

## Description
A web-based attendance management system that leverages QR codes for efficient and secure attendance marking. The system provides separate dashboards for admins and users, allowing for easy attendance tracking, user management, and QR code generation.

## Features
- User registration and authentication
- Admin and user dashboards
- QR code generation for attendance
- Attendance marking via QR code scanning
- Attendance directory and reports
- Profile management
- Request handling for admins

## Technologies Used
- **Backend:** Python (Flask)
- **Frontend:** HTML, CSS, JavaScript (Jinja2 templating)
- **Database:** (Specify here, e.g., SQLite/MySQL/PostgreSQL)
- **Other:** QR code generation library

## Setup Instructions
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Full-Stack-Attendance-System-with-QR-Code/attendance-system
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application:**
   ```bash
   python app.py
   ```
4. **Access the app:**
   Open your browser and go to `http://localhost:5000`

## Usage
- **Sign up** as a new user or log in if you already have an account.
- **Admins** can view attendance records, manage users, and handle requests.
- **Users** can mark attendance by scanning QR codes and view their attendance history.

## Folder Structure
```
Full-Stack-Attendance-System-with-QR-Code/
  └── attendance-system/
      ├── app.py
      └── templates/
          ├── admin_attendance.html
          ├── admin_dashboard.html
          ├── admin_requests.html
          ├── attendance_directory.html
          ├── dashboard.html
          ├── download_qr.html
          ├── home.html
          ├── login.html
          ├── mark_attendance.html
          ├── profile.html
          └── signup.html
```

