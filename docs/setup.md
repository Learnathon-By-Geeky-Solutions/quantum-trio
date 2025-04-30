# CareHub Development Setup Guide

This guide provides step-by-step instructions to set up the **CareHub** project locally for development. Follow these steps to clone the repository, configure the environment, and run the application.

---

## Prerequisites

Before setting up the project, ensure you have the following tools installed:

- **Python** (version 3.8 or higher): [Download Python](https://www.python.org/downloads/)
- **PostgreSQL** (version 12 or higher): [Download PostgreSQL](https://www.postgresql.org/download/)
- **Git**: [Download Git](https://git-scm.com/downloads)
- **pip**: Python package manager (comes with Python)
- **Virtualenv** (optional, but recommended): For creating isolated Python environments
- **Node.js** (optional, for frontend asset compilation if needed): [Download Node.js](https://nodejs.org/)

---

## Step-by-Step Setup

### 1. Clone the Repository

Clone the CareHub repository from GitHub to your local machine:

```bash
git clone https://github.com/Learnathon-By-Geeky-Solutions/quantum-trio.git
cd quantum-trio
```

---

### 2. Set Up a Virtual Environment (Optional but Recommended)

Create and activate a virtual environment to manage Python dependencies:

```bash
# Install virtualenv if not already installed
pip install virtualenv

# Create a virtual environment
virtualenv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt, indicating the virtual environment is active.

---

### 3. Install Python Dependencies

Install the required Python packages listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

This will install dependencies like Django, psycopg2 (for PostgreSQL), and other project-specific packages.

---

### 4. Configure PostgreSQL Database

1. **Install PostgreSQL**: Ensure PostgreSQL is installed and running on your system.
2. **Create a Database**:
   - Open the PostgreSQL command-line tool (`psql`) or a GUI tool like pgAdmin.
   - Create a new database for CareHub:

     ```sql
     CREATE DATABASE carehub;
     ```

3. **Verify Database Access**:
   - Ensure you have a PostgreSQL user with the necessary privileges.
   - Note the database name, username, password, host, and port (default is `5432`).

---

### 5. Set Up Environment Variables

Create a `.env` file in the project root directory to store sensitive configuration settings. Use the following template:

```env
# Django settings
SECRET_KEY=your-django-secret-key
DEBUG=True

# Database settings
DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/carehub

# Other optional settings
ALLOWED_HOSTS=localhost,127.0.0.1
```

- **SECRET_KEY**: Generate a secure key for Django (e.g., using a random string generator).
- **DATABASE_URL**: Replace `<username>`, `<password>`, `<host>`, and `<port>` with your PostgreSQL credentials.
- **DEBUG**: Set to `True` for development, `False` for production.

You can use a package like `python-decouple` to load these variables in your Django settings. Ensure it’s installed:

```bash
pip install python-decouple
```

---

### 6. Apply Database Migrations

Run the following commands to apply Django migrations and set up the database schema:

```bash
python manage.py makemigrations
python manage.py migrate
```

This will create the necessary tables in the `carehub` database based on the project’s models.

---

### 7. Create a Superuser (Optional)

Create an admin user to access the Django admin panel:

```bash
python manage.py createsuperuser
```

Follow the prompts to set up a username, email, and password for the superuser.

---

### 8. Install Frontend Dependencies (If Applicable)

If the project requires frontend asset compilation (e.g., Tailwind CSS or JavaScript bundling), install Node.js dependencies:

```bash
npm install
```

Run any necessary build commands (e.g., for Tailwind CSS):

```bash
npm run build
```

Check the project’s `package.json` for specific scripts.

---

### 9. Run the Development Server

Start the Django development server to test the application locally:

```bash
python manage.py runserver
```

Open your browser and navigate to `http://127.0.0.1:8000/` to view the CareHub application.

---

### 10. Verify the Setup

- Access the homepage at `http://127.0.0.1:8000/`.
- Log in to the Django admin panel at `http://127.0.0.1:8000/admin/` using the superuser credentials.
- Test key features like user authentication, booking, and shop management.

---

## Troubleshooting

- **Database Connection Issues**:
  - Verify PostgreSQL is running and the `DATABASE_URL` in `.env` is correct.
  - Ensure the PostgreSQL user has proper permissions for the `carehub` database.
- **Missing Dependencies**:
  - Run `pip install -r requirements.txt` again to ensure all packages are installed.
  - Check for version conflicts and resolve them by updating `requirements.txt`.
- **Frontend Issues**:
  - Ensure Node.js and npm are installed if frontend assets fail to load.
  - Run `npm install` and `npm run build` to regenerate assets.
- **Port Conflicts**:
  - If port `8000` is in use, run the server on a different port:
    ```bash
    python manage.py runserver 8080
    ```

---

## Running Tests

To ensure the application is functioning correctly, run the test suite:

```bash
python manage.py test
```

This will execute unit and integration tests defined in the project.

---

## Additional Notes

- **Static Files**: If static files (CSS, JavaScript, images) are not loading, collect them to the static directory:
  ```bash
  python manage.py collectstatic
  ```
- **Production Setup**: For production, set `DEBUG=False` in `.env`, configure a production-grade web server (e.g., Gunicorn), and use a reverse proxy like Nginx.
- **Documentation**: Refer to the [Project Wiki](https://github.com/Learnathon-By-Geeky-Solutions/quantum-trio/wiki) for additional details on project structure and workflows.

---

## Need Help?

If you encounter issues or have questions, reach out to the Quantum Trio team:

- **GitHub Issues**: [Create an issue](https://github.com/Learnathon-By-Geeky-Solutions/quantum-trio/issues)
- **Email**: [quantum.trio@example.com](mailto:quantum.trio@example.com)

---

<p align="center">
  Happy coding with CareHub! 🚀
</p>