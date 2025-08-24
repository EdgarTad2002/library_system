# Use a slim Python image for a smaller final size
FROM python:3.10-slim

# Set the working directory
WORKDIR /usr/src/app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project's source code
COPY . .

# Copy the startup script into the container
COPY start.sh .

# Make the startup script executable inside the container
RUN chmod +x start.sh


# Use the startup script as the entrypoint for the container
ENTRYPOINT ["./start.sh"]

CMD ["./start.sh"]
