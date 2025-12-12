# Use a lightweight Python version
FROM python:3.11-slim

# Install FFmpeg (The magic step)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Set up the folder
WORKDIR /app

# Copy files
COPY . .

# Install Python libraries
RUN pip install --no-cache-dir -r requirements.txt

# Run the bot
CMD ["python", "bot.py"]