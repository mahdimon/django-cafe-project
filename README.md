# DJANGO-CAFE-PROJECT

> It is a website that simulates a coffee shop.

---

## Table of Contents
- [About the Project](#about-the-project)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation and Setup](#installation-and-setup)
- [Usage](#usage)
- [Folder Structure](#folder-structure)
- [Additional Information](#additional-information)
- [License](#license)

---

## About the Project
  It is a website that simulates a coffee shop.where you can register an order and make menu with both the staff panel and the customer panel.
  And there is an analysis panel that can be used to analyze the coffee shop

### Example
This project is a web application built with Django that helps users manage coffee shop. It includes features like user authentication, order ,checkout , and analytics panel.

---

## Features
- User registration
- Item creation, editing, and deletion
- creating orders and manage the orders
- Responsive design for desktop and mobile
- Including 3 panels (customer/staff/analytics)
- Connected to Postgresql

---

## Prerequisites
Make sure the following are installed on your machine:
- **Python 3.x** 
- **Django** (version required for this project, e.g., Django 4.0)
- **pip** (Python package installer)
- **virtualenv** (optional, but recommended for environment isolation)

---

## Installation and Setup
1. **Clone the repository:**
    ```bash
    git clone https://github.com/mahdimon/django-cafe-project.git
    cd django-cafe-project
    ```

2. **Create a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Apply migrations to set up the database:**
    ```bash
    python manage.py migrate
    ```

5. **Create a superuser (optional, for accessing the admin panel):**
    ```bash
    python manage.py createsuperuser
    ```

6. **Run the development server:**
    ```bash
    python manage.py runserver
    ```

Your project should now be accessible at `http://127.0.0.1:8000/`.

---

## Usage
Provide instructions on how to use the project once it’s running. You could include information about:
- Logging in
- Using specific features
- Accessing the staff panel=

---

## Folder Structure
Here’s an overview of the main folders and files in the project:

django-cafe-project/
├───analytics
│   ├───templates
│   │   └───analytics
│   └───__pycache__
├───cafe
│   └───__pycache__
├───core
│   ├───migrations
│   │   └───__pycache__
│   └───__pycache__
├───customer
│   ├───migrations
│   │   └───__pycache__
│   ├───templates
│   │   └───customer
│   ├───templatetags
│   │   └───__pycache__
│   └───__pycache__
├───media
│   └───images
├───staff
│   ├───migrations
│   │   └───__pycache__
│   ├───templates
│   │   └───staff
│   └───__pycache__
├───static
│   └───images
└───templates