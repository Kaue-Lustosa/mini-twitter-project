FROM python:3.9

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install netcat for the entrypoint script
RUN apt-get update && apt-get install -y netcat-openbsd

# Copy project
COPY . .

# Make scripts executable
RUN chmod +x manage.py
RUN chmod +x entrypoint.sh
RUN chmod +x run_migrations.py

# Expose port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["./entrypoint.sh"]

# Command to run when container starts
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]