FROM python:3.6.10-buster

# Make a directory for the application
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip  install -r requirements.txt

ADD ./DockerResources/channels_presence /usr/local/lib/python3.6/site-packages/channels_presence

# Copy project files
COPY . .

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]