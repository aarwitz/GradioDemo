# Use the official Python image as the base image
FROM python:3.8

# Set the working directory inside the container
WORKDIR /app

# Copy the application files to the container
COPY app.py /app/
COPY requirements.txt /app/
COPY example.jpg /app/
COPY launch_inference.py /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that Gradio will run on
# EXPOSE 7860

# Run the application
CMD ["python", "app.py"]

