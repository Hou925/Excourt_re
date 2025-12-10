# School Court Booking API

A Flask-based REST API for managing school court bookings across multiple campuses.

## Overview

This API provides functionality for managing court bookings in a school environment. It supports multiple campuses and allows students to book courts for specific dates and times.

## Features

- Student management (registration, authentication)
- Court booking system
- Multiple campus support (JiaDing, SiPing, Huxi, HuBei)
- QR code generation for court bookings
- PostgreSQL database integration

## Database Schema

### Students Table
- Student_id (Primary Key)
- Student_name
- Student_phone
- Student_password

### Court Information Table
- Court_id (Primary Key)
- Court_campus (Enum: JiaDing, SiPing, Huxi, HuBei)
- Court_date
- Court_time
- Court_no
- Court_state (Enum: not_owned, owned)
- Court_owner (Foreign Key to Student)
- Court_qrcodeurl

## Prerequisites

- Python 3.x
- PostgreSQL
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
  git clone [repository-url]
  cd SchoolAPI
```

2. Create and activate a virtual environment:
```bash
  python -m venv venv
  source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
  pip install -r requirements.txt
```

4. Set up the database:
```bash
  psql -U your_username -d your_database -f SchoolAPI.sql
```

5. Configure environment variables:
Create a `.env` file in the root directory with necessary configuration.

## Running the Application

```bash
  python app.py
```

The API will be available at `http://localhost:5000`

## Dependencies

- Flask==3.0.2
- psycopg2-binary==2.9.9
- python-dotenv==1.0.1
- Werkzeug==3.0.1
- marshmallow==3.20.2
- black==24.2.0
- isort==5.13.2

## Development

The project uses:
- Black for code formatting
- isort for import sorting
- PostgreSQL for database management