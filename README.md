# Django Engine Module

This project is a modular Django application that demonstrates a plug-in style engine with module discovery, middleware, signals, and templating. It includes a sample `product` module and a core `engine` app.

## Project Structure

- engine/: Core engine app providing module loading and related functionality
- modules/: Pluggable modules (example: product)
- enginemoduledoni/: Django project settings and root URLs
- manage.py: Django management entry point

## Requirements

- Python 3.10+
- pip3
- (Optional) Docker and Docker Compose

Install Python dependencies:

```
pip3 install -r requirements.txt
```

Copy environment variables (adjust as needed):

```
cp .env.example .env
```

## Database Migrations

Create migrations for the `engine` app:

```
python3 manage.py makemigrations engine
```

Apply migrations:

```
python3 manage.py migrate
```

## Running the Development Server

```
python3 manage.py runserver --noreload
```

Then open http://127.0.0.1:8000/ in your browser.

## Using Docker (Optional)

Build and run with Docker Compose:

```
docker compose up --build
```

## License

This project is provided as-is for demonstration purposes by DoniHMRs