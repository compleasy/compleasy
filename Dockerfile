FROM python:3.8-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the content of the local src directory to the working directory
COPY src/* .

# Install pip
RUN pip install --upgrade pip

# Install any dependencies
RUN pip install -r requirements.txt

# Specify the command to run on container start
CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]

# Export the port
EXPOSE 8000