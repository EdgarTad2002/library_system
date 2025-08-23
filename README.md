# Library Management System

This project is a Django-based web application designed for managing a library. It allows you to list books, categorize them, and handle other related library functionalities. The entire application is containerized using Docker, making it easy to set up and run consistently across different environments.

## Features

* **Book Management**: Add, view, update, and delete book records.
* **Category Management**: Organize books into various categories.
* **User Authentication**: (Implied by `djoser`) User registration and login functionality.
* **Performance Profiling**: (Implied by `django-silk`) Integrated with Django Silk for request profiling and optimization.
* **Scheduled Tasks**: (Implied by `django-crontab`) Ability to run scheduled tasks.

## Getting Started

To get this project up and running, you'll need Docker installed on your machine.

### Prerequisites

* [**Docker Desktop**](https://www.docker.com/products/docker-desktop) (for Windows/macOS) or [**Docker Engine**](https://docs.docker.com/engine/install/) (for Linux)

### Installation and Setup

Follow these steps to set up and run the project:

1.  **Clone the repository**:
    ```bash
    git clone [https://github.com/EdgarTad2002/library_system.git](https://github.com/EdgarTad2002/library_system.git)
    cd library_system
    ```

2.  **Configure Environment Variables**:
    Your project uses environment variables for sensitive settings (like `SECRET_KEY`) and external services (like email credentials). We've provided an example file.

    * Create your `.env` file by copying the provided example:
        ```bash
        cp .env.example .env
        ```
    * Open the newly created `.env` file in your text editor (`nano .env` or equivalent).
    * **`SECRET_KEY`**: Replace `your_django_secret_key_here` with a unique, long, and random string. You can generate one using the Django shell:
        ```bash
        python manage.py shell
        # >>> from django.core.management.utils import get_random_secret_key
        # >>> print(get_random_secret_key())
        # >>> exit()
        ```
        Copy the output and paste it into your `.env` file.
    * **`EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`**: Replace the placeholder values with your actual email address and a generated "App Password" from your email provider (e.g., Google App Passwords for Gmail). **Do not use your main email password.**

3.  **Build and Run the Docker Containers**:
    This command will build the Docker image, apply necessary database migrations, load initial sample data, and start the Django development server.

    ```bash
    docker compose up --build
    ```
    (The `--build` flag is important the first time you run it, or after any changes to `Dockerfile`, `requirements.txt`, or `start.sh`.)

4.  **Access the Application**:
    Once the containers are running (you'll see Django server logs in your terminal), open your web browser and navigate to:

    `http://localhost:8000`

    You should see the home page of the Library Management System, pre-populated with example data.

### Initial Data

The project includes an `initial_data.json` fixture file. When you run `docker compose up --build`, the `start.sh` script automatically runs `python manage.py loaddata initial_data.json` to populate your database with sample books and categories, allowing you to see the project's functionality immediately.

## Development Workflow

* **Code Changes**: Work on your Python code locally in your virtual environment. Thanks to Docker volumes, changes will instantly reflect in the running container.
* **Database Model Changes**: If you modify `models.py`:
    1.  Run `docker exec -it library_system-web-1 python manage.py makemigrations` to create new migration files.
    2.  Commit these new migration files to Git.
    3.  The next time the container starts (or if you restart it), `migrate` will be run automatically.
* **New Dependencies**: If you add new packages:
    1.  Install them in your local virtual environment: `pip install new-package`.
    2.  Add them to `requirements.txt` with their version.
    3.  Run `docker compose up --build` to rebuild the image with the new dependencies.

---