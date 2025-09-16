# Pre-Course Setup Guide

Welcome! This guide will help you set up your local environment for the course. Following these steps before the first session will ensure you can hit the ground running.

If you run into any issues, please don't hesitate to reach out.

## Prerequisites

### System Requirements
- **RAM**: At least 8GB (16GB recommended)
- **Disk Space**: At least 5GB free space
- **Estimated Setup Time**: 15-30 minutes (depending on internet speed)

### Required Software

You will need the following software installed on your machine:

1.  **Python (up to 3.13)**: The course materials are compatible with Python versions up to 3.13.

    - **To check your version**: `python3 --version`
    - **To install**: Visit the official [Python website](https://www.python.org/downloads/).

2.  **Docker Desktop**: We will use Docker to run a PostgreSQL database (with the `pgvector` extension) and an Ollama server for local embeddings.
    - **To install**: Visit the [Docker website](https://www.docker.com/products/docker-desktop/).
    - **Required Ports**: 5050 (PostgreSQL), 11434 (Ollama)
    - **Note**: Docker Desktop must be running before starting the services.

## Setup Instructions

### Step 1: Unpack the Zip File

This README.md is part of a zip file with everything you need to get started with our course.

1. **Unzip the file** to a location of your choice (e.g., your Desktop or Documents folder)
2. **Navigate to the extracted folder** in your terminal/command prompt
3. **Verify you're in the right directory** by checking that you can see these files:
   - `PRECOURSE_SETUP.md` (this file)
   - `requirements.txt`
   - `verify_setup.py`
   - `environment/` directory

If you can see these files, you're in the correct project root directory.

### Step 2: Install Python Dependencies

It is highly recommended to use a Python virtual environment to avoid conflicts with other projects. A virtual environment creates an isolated Python environment for this course.

```bash
# 1. Create a virtual environment
python3 -m venv .venv

# 2. Activate the virtual environment
# On macOS and Linux:
source .venv/bin/activate
# On Windows:
# .\.venv\Scripts\activate

# 3. Install the required packages
pip install -r requirements.txt
```

**Important Notes:**
- You'll need to activate this virtual environment each time you work on the course: `source .venv/bin/activate` (macOS/Linux) or `.\\.venv\\Scripts\\activate` (Windows)
- To deactivate the virtual environment when you're done: `deactivate`

### Step 3: Start the Docker Services

The services are defined in a `compose.yml` file located in the `environment/` directory. This will start:
- **PostgreSQL database** with the `pgvector` extension (for vector embeddings)
- **Ollama service** (for running embedding models locally)

```bash
# Navigate to the environment directory
cd environment

# Start the services in the background
docker compose up -d
```

This command will download the necessary Docker images and start the containers. This may take a few minutes the first time.

**Troubleshooting:**
- If you get permission errors, make sure Docker Desktop is running
- If ports are already in use, check if you have other services running on ports 5050 or 11434

### Step 4: Download the Embedding Model

The Ollama service needs to download the `bge-m3` embedding model (~2GB), which we'll use throughout the course.

First, find the name of your Ollama container:

```bash
docker ps
```

Look for a container with `ollama` in the name. It should be `ollama-service`.

Now, run the following command, replacing `<container_name>` with the name you found:

```bash
# Example: docker exec ollama-service ollama pull bge-m3
docker exec <container_name> ollama pull bge-m3
```

**Alternative method** (if the above doesn't work):
```bash
# Use the container ID instead of name
docker exec $(docker ps -q --filter "ancestor=ollama/ollama") ollama pull bge-m3
```

This download is approximately 2GB and may take 5-15 minutes depending on your internet connection.

### Step 5: Verify Your Setup

To make sure everything is working correctly, run the provided verification script from the root directory of the project.

```bash
# Make sure you are in the root directory of the project
# (where you can see PRECOURSE_SETUP.md, requirements.txt, etc.)
# and your virtual environment is activated.

# If you're in the environment/ directory, go up one level:
cd ..

# Run the verification script
python verify_setup.py
```

The script will check your Python version, database connection, and the Ollama embedding service. If all checks pass, you'll see a success message. If not, it will provide error messages to help you troubleshoot.

### Environment Variables (Optional)

The verification script uses default configuration, but you can customize it by creating a `.env` file in the project root:

```bash
# Create .env file (optional)
cat > .env << EOF
DB_NAME=pgvector
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5050
OLLAMA_URL=http://localhost:11434/api/embed
EOF
```

## Troubleshooting

### Common Issues

**Docker Services Won't Start:**
- Ensure Docker Desktop is running
- Check if ports 5050 or 11434 are already in use: `lsof -i :5050` (macOS/Linux) or `netstat -an | findstr :5050` (Windows)
- Try restarting Docker Desktop

**Database Connection Failed:**
- Verify Docker services are running: `docker ps`
- Check Docker logs: `docker logs pgvector-db`
- Ensure you're using the correct port (5050, not 5432)

**Ollama Model Not Found:**
- Verify the model was downloaded: `docker exec ollama-service ollama list`
- Re-download the model: `docker exec ollama-service ollama pull bge-m3`
- Check Ollama logs: `docker logs ollama-service`

**Python Virtual Environment Issues:**
- Make sure you're in the project root directory
- Verify the virtual environment is activated (you should see `(.venv)` in your prompt)
- Try recreating the virtual environment: `rm -rf .venv && python3 -m venv .venv`

**Permission Errors:**
- On macOS/Linux, you might need to use `sudo` for Docker commands
- Ensure your user is in the `docker` group

### Getting Help

If you're still having issues:
1. Check the Docker logs: `docker logs <container_name>`
2. Verify all services are running: `docker ps`
3. Try restarting the services: `docker compose down && docker compose up -d`
4. Reach out for help with specific error messages

## Next Steps

Once your setup is verified:
- **Starting services**: `cd environment && docker compose up -d`
- **Stopping services**: `cd environment && docker compose down`
- **Reactivating environment**: `source .venv/bin/activate` (from project root)
- **Checking service status**: `docker ps`

---

You're all set! We look forward to seeing you in the course.
