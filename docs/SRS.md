# Software Requirements Specification (SRS) for CareHub

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) document outlines the functional and non-functional requirements for CareHub, a beauty and wellness booking platform developed by Team Quantum Trio for Learnathon 3.0. The platform aims to streamline salon and grooming experiences in Bangladesh by providing smart booking, filtering, and management tools.

### 1.2 Scope

CareHub is a web-based platform designed to modernize the beauty and wellness service industry by addressing challenges such as long wait times, inaccessible providers, lack of real-time availability, and manual booking processes. The system offers features for customers, shop owners, and administrators, including booking management, real-time notifications, a RAG-based chatbot, and a transparent feedback system.

### 1.3 Definitions, Acronyms, and Abbreviations

- **CareHub**: The beauty and wellness booking platform.
- **Customer**: An end-user who books services.
- **Shop Owner**: A service provider managing a salon or wellness business.
- **Admin**: A system administrator overseeing platform operations.
- **RAG**: Retrieval-Augmented Generation, a method for enhancing chatbot responses using external data.
- **Django**: A Python-based web framework used for backend development.
- **PostgreSQL**: The relational database management system used.
- **Tailwind CSS**: A utility-first CSS framework for frontend styling.

### 1.4 References

- GitHub Wiki: https://github.com/Learnathon-By-Geeky-Solutions/quantum-trio/wiki
- Project Repository: https://github.com/Learnathon-By-Geeky-Solutions/quantum-trio
- Asana Project Board: CareHub Board (referenced in wiki)

### 1.5 Overview

This SRS document is structured to provide a comprehensive understanding of CareHub’s requirements. It includes system features, external interface requirements, functional and non-functional requirements, and other specifications to guide development and testing.

## 2. Overall Description

### 2.1 Product Perspective

CareHub is a standalone web application that integrates frontend, backend, and database components to facilitate beauty and wellness service bookings. It operates as a centralized platform connecting customers with service providers while providing administrative oversight.

### 2.2 Product Functions

- **User Authentication**: Secure login/signup for customers and shop owners.
- **Customer Dashboard**: Manage bookings, preferences, and profiles.
- **Shop Profile Management**: Define services, pricing, location, and worker details.
- **Advanced Booking System**: Book services with real-time date/time slots and expert selection.
- **Filtering System**: Search services by location, price, ratings, or service type.
- **Ratings & Reviews**: Transparent feedback system post-service completion.
- **General RAG-Based Chatbot**: Assist users with queries using a retrieval-augmented generation model.
- **Notifications**: Real-time alerts for booking updates and confirmations.
- **Digital Payment Slip**: Auto-generated receipts upon booking confirmation.
- **Booking Reports**: Analytics for customers and shop owners.
- **Admin Panel**: Manage users, shops, and reviews.
- **Order Confirmation**: Dual approval system for bookings.
- **Post-Service Feedback**: Rate and review services after completion.

### 2.3 User Classes and Characteristics

- **Customers**:
  - Individuals seeking beauty and wellness services.
  - Require an intuitive interface for booking, filtering, and interacting with a chatbot.
  - Expected to have basic internet and device proficiency.
- **Shop Owners**:
  - Service providers managing salons or wellness centers.
  - Need tools to manage services, bookings, and employee schedules.
  - Expected to have moderate technical proficiency.
- **Administrators**:
  - Platform overseers ensuring system integrity and user satisfaction.
  - Require advanced tools for user and content management.
  - Expected to have high technical proficiency.

### 2.4 Operating Environment

- **Client-Side**: Web browsers (Chrome, Firefox, Safari) on desktops, tablets, or smartphones.
- **Server-Side**: Django-based backend hosted on a cloud server (e.g., AWS, Heroku).
- **Database**: PostgreSQL for data storage and management.
- **Network**: Reliable internet connection for real-time updates and chatbot functionality.

### 2.5 Design and Implementation Constraints

- **Technology Stack**: Limited to HTML, Tailwind CSS, JavaScript (frontend), Django (backend), and PostgreSQL (database).
- **Scalability**: Must handle at least 1,000 concurrent users initially.
- **Security**: Must comply with basic data protection standards (e.g., secure storage of passwords and payment details).
- **Localization**: Focused on Bangladesh, with potential for regional expansion.

### 2.6 Assumptions and Dependencies

- **Assumptions**:
  - Users have access to modern web browsers and stable internet.
  - Shop owners are willing to adopt digital tools for service management.
- **Dependencies**:
  - Django and PostgreSQL for core functionality.
  - Asana for project management.
  - External libraries listed in `requirements.txt`.
  - RAG-based chatbot model and associated data sources.

## 3. External Interface Requirements

### 3.1 User Interfaces

- **Customer Interface**:
  - Dashboard displaying bookings, profile, and preferences.
  - Search and filter interface for services.
  - Chatbot interface for user queries.
- **Shop Owner Interface**:
  - Dashboard for managing services, bookings, and employee schedules.
  - Analytics reports for business insights.
- **Admin Interface**:
  - Panel for managing users, shops, and reviews.
  - Tools for monitoring system performance and chatbot interactions.

### 3.2 Hardware Interfaces

- No specific hardware interfaces are required beyond standard client devices (PCs, smartphones, tablets).

### 3.3 Software Interfaces

- **Frontend**: HTML, Tailwind CSS, JavaScript for rendering and interactivity.
- **Backend**: Django for handling requests, authentication, and business logic.
- **Database**: PostgreSQL for storing user data, bookings, and reviews.
- **Chatbot**: RAG-based model integrated with Django for query handling.
- **External APIs** (if applicable): Payment gateways for processing transactions.

### 3.4 Communications Interfaces

- **HTTP/HTTPS**: For secure client-server communication.
- **WebSockets** (optional): For real-time chatbot interactions.
- **SMTP**: For email notifications (e.g., booking confirmations).

## 4. System Features

### 4.1 User Authentication

- **Description**: Secure login and signup for customers and shop owners.
- **Priority**: High
- **Functional Requirements**:
  - Users can register with email, password, and role (customer/shop owner).
  - Login with email and password, with password recovery option.
  - Role-based access control for dashboards.
- **Non-Functional Requirements**:
  - Passwords must be hashed and stored securely.
  - Authentication must complete within 2 seconds.

### 4.2 Customer Dashboard

- **Description**: Interface for customers to manage bookings and profiles.
- **Priority**: High
- **Functional Requirements**:
  - View and edit profile details (name, contact, preferences).
  - View upcoming and past bookings.
  - Cancel or reschedule bookings (subject to shop policies).
- **Non-Functional Requirements**:
  - Dashboard must load within 3 seconds.
  - Responsive design for mobile and desktop.

### 4.3 Shop Profile Management

- **Description**: Tools for shop owners to manage services and schedules.
- **Priority**: High
- **Functional Requirements**:
  - Add/edit services, pricing, and availability.
  - Manage employee details and schedules.
  - Upload shop images and descriptions.
- **Non-Functional Requirements**:
  - Support for up to 50 services per shop.
  - Image uploads limited to 5MB per file.

### 4.4 Advanced Booking System

- **Description**: Book services with real-time availability and expert selection.
- **Priority**: High
- **Functional Requirements**:
  - Display available time slots for selected services.
  - Allow selection of specific stylists or experts.
  - Dual approval system (customer and shop) for booking confirmation.
- **Non-Functional Requirements**:
  - Real-time updates with &lt;1-second latency.
  - Handle up to 100 simultaneous booking requests.

### 4.5 Filtering System

- **Description**: Search services by location, price, ratings, or type.
- **Priority**: Medium
- **Functional Requirements**:
  - Filter services by multiple criteria.
  - Sort results by relevance, price, or ratings.
  - Save frequently used filters.
- **Non-Functional Requirements**:
  - Search results must load within 2 seconds.
  - Support for at least 1,000 service listings.

### 4.6 Ratings & Reviews

- **Description**: Transparent feedback system for services.
- **Priority**: Medium
- **Functional Requirements**:
  - Customers can rate and review services post-completion.
  - Shop owners can respond to reviews.
  - Reviews are visible to all users.
- **Non-Functional Requirements**:
  - Reviews must be moderated for inappropriate content.
  - System must handle up to 10,000 reviews.

### 4.7 General RAG-Based Chatbot

- **Description**: A chatbot using Retrieval-Augmented Generation to assist users with general queries.
- **Priority**: Medium
- **Functional Requirements**:
  - Answer questions about services, bookings, and platform usage.
  - Retrieve relevant information from a predefined knowledge base.
  - Provide responses in natural language based on user input.
- **Non-Functional Requirements**:
  - Response time &lt;2 seconds for 95% of queries.
  - Handle up to 500 concurrent chatbot sessions.
  - Chat history stored for 30 days.

### 4.8 Notifications

- **Description**: Real-time alerts for booking updates.
- **Priority**: High
- **Functional Requirements**:
  - Notify customers and shops of booking confirmations, cancellations, or changes.
  - Support for in-app and email notifications.
- **Non-Functional Requirements**:
  - Notifications delivered within 5 seconds.
  - Handle up to 1,000 notifications per minute.

### 4.9 Digital Payment Slip

- **Description**: Auto-generated receipts for confirmed bookings.
- **Priority**: Medium
- **Functional Requirements**:
  - Generate PDF receipts with booking details.
  - Allow download or email delivery of receipts.
- **Non-Functional Requirements**:
  - Receipt generation within 3 seconds.
  - Receipts stored for 90 days.

### 4.10 Admin Panel

- **Description**: Centralized control for platform management.
- **Priority**: High
- **Functional Requirements**:
  - Manage user accounts (suspend, delete, or edit).
  - Monitor shop listings and reviews.
  - View system analytics (e.g., booking trends).
- **Non-Functional Requirements**:
  - Admin panel must be accessible only to authorized users.
  - Load time &lt;5 seconds for all views.

## 5. Other Non-Functional Requirements

### 5.1 Performance Requirements

- System must support 1,000 concurrent users with &lt;5-second response times.
- Database queries must execute within 1 second for 95% of operations.
- Chatbot responses must be generated within 2 seconds.

### 5.2 Security Requirements

- Use HTTPS for all communications.
- Store sensitive data (e.g., passwords, payment details) encrypted.
- Implement CSRF and XSS protection in Django.

### 5.3 Quality Attributes

- **Usability**: Intuitive interface with &lt;5-minute learning curve for new users.
- **Reliability**: System uptime of 99.9%.
- **Scalability**: Handle 10,000 users within 6 months of launch.

### 5.4 Business Rules

- Shops must verify their identity before listing services.
- Customers can only review services they have booked and completed.
- Refunds or cancellations follow shop-specific policies.

## 6. Other Requirements

### 6.1 Database Requirements

- PostgreSQL database with tables for users, shops, bookings, reviews, and chatbot interactions.
- Regular backups every 24 hours.
- Data retention for 1 year (except chatbot interactions, 30 days).

### 6.2 Legal Requirements

- Comply with Bangladesh’s data protection laws.
- Include terms of service and privacy policy in the platform.

### 6.3 Localization Requirements

- Support for English and Bengali languages.
- Currency in Bangladeshi Taka (BDT).

## 7. Appendices

### 7.1 Project Repository Structure

```
quantum-trio/
├── booking/              # Service booking logic
├── carehub/              # Django project configuration
├── my_app/               # Common functionalities
├── registration/         # User registration and login
├── shop_profile/         # Shop management
├── user_profile/         # Customer management
├── static/               # CSS, JS, icons
├── templates/            # HTML templates
├── theme/                # Design assets
├── media/                # Uploaded media
├── venv/                 # Virtual environment
├── .env                  # Environment variables
├── .gitignore            # Git ignored files
├── .hintrc               # Linting configuration
├── CareHUB.drawio.png    # Architecture diagram
├── LICENSE               # Open source license
├── manage.py             # Django manager script
├── Pipfile               # Dependency tracker
├── README.md             # Project overview
├── requirements.txt      # Python dependencies
```

### 7.2 Environment Variables

```
DJANGO_SECRET_KEY=<your-secret-key>
DATABASE_PASSWORD=<your-db-password>
```

### 7.3 Team Information

- **Team**: Quantum Trio
- **Members**: Israt Jahan Reshma (Leader), Md Rakibul Islam, Asfak Shahriur
- **Mentor**: Rajesh Saha
