
FROM python:3.9

# Install system dependencies for audio (libsndfile is required by librosa)
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /code

# Copy requirements first to cache installation
COPY requirements.txt .

# Install dependencies
# We pin version numbers to ensure compatibility
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    "flask" \
    "tensorflow==2.15.0" \
    "numpy<2.0" \
    "librosa==0.10.1" \
    "scikit-learn" \
    "gunicorn"

# Copy all files
COPY . .

# IMPORTANT: Create a non-root user (Hugging Face requirement)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Expose port (Hugging Face expects 7860)
EXPOSE 7860

# Add nested folder to Python Path so it can find 'src'
ENV PYTHONPATH="${PYTHONPATH}:/code/finalminorproject"

# Force Python output to be unbuffered (Crucial for Logs)
ENV PYTHONUNBUFFERED=1

# Command to run the application using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:7860", "src.server_app:app"]
