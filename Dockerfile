FROM python:3.12-slim

# Install system dependencies
# - curl for healthchecks
# - WeasyPrint dependencies: pango, cairo, gobject, gdk-pixbuf, shared-mime-info
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    shared-mime-info \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Copy the entrypoint
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Set the working directory in the container
WORKDIR /app

# Copy the content of the local src directory to the working directory
COPY src/* .

# Install pip
RUN pip install --upgrade pip

# Install any dependencies
RUN pip install -r requirements.txt

# Export the port
EXPOSE 8000

# Run the entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]