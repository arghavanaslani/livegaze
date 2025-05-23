FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy flask_app into the container
COPY flask_app /app/flask_app


# Expose the port Flask/Gunicorn will run on
EXPOSE 5100

# Command to run Gunicorn
CMD ["gunicorn", "-k", "eventlet","-c", "flask_app/gunicorn_config.py", "flask_app.app:app", "-b", "0.0.0.0:5100"]
