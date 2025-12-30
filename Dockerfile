# =============================================================================
# DOCKER CORE CONCEPTS
# =============================================================================

# WHAT IS DOCKER?
# Docker is a platform that packages applications and their dependencies into 
# standardized units called containers, ensuring consistent behavior across 
# different environments (dev, staging, production).

# WHY USE DOCKER?
# 1. CONSISTENCY: "Works on my machine" problem solved - same environment everywhere
# 2. ISOLATION: Each container runs independently without conflicts
# 3. PORTABILITY: Run anywhere - local, cloud, any OS that supports Docker
# 4. EFFICIENCY: Lightweight compared to VMs (shares host OS kernel)
# 5. SCALABILITY: Easy to replicate and scale containers
# 6. VERSION CONTROL: Track changes to your environment over time

# DOCKER DAEMON (dockerd):
# - Background service running on the host machine
# - Manages Docker objects (images, containers, networks, volumes)
# - Listens for Docker API requests and executes them
# - Builds, runs, and distributes containers

# DOCKERFILE:
# - Text file with instructions to build a Docker image
# - Contains commands like FROM, COPY, RUN, CMD, EXPOSE
# - Blueprint for creating images
# - Defines the environment and application setup

# DOCKER IMAGE:
# - Read-only template used to create containers
# - Built from Dockerfile using "docker build" command
# - Contains OS, application code, dependencies, configuration
# - Layered architecture (each instruction creates a new layer)
# - Can be shared via Docker Hub or private registries

# DOCKER CONTAINER:
# - Running instance of an image
# - Isolated, lightweight, and executable package
# - Contains everything needed to run the application
# - Can be started, stopped, moved, and deleted
# - Multiple containers can run from the same image

# ANALOGY:
# - Dockerfile = Recipe
# - Image = Cake (prepared but not consumed)
# - Container = Slice of cake being eaten (active instance)

# =============================================================================
# DOCKERFILE FOR FASTAPI APPLICATION
# =============================================================================

# STEP 1: Define base image
# FROM specifies the parent image to build upon
# python:3.11-slim is a lightweight Python image (~50MB smaller than full image)
# "slim" variant includes only essential packages
FROM python:3.11-slim

# STEP 2: Copy requirements file first
# This leverages Docker's layer caching
# If requirements.txt hasn't changed, Docker uses cached layer (faster builds)
# The dot (.) means copy to /app directory inside container (current WORKDIR)
COPY ./requirements.txt .

# STEP 3: Install Python dependencies
# RUN executes commands during image build
# pip install reads requirements.txt and installs all listed packages
# Upgrade pip first for better dependency resolution
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Alternative: No-cache installation (smaller image size, slower build)
# Use this if you want to minimize image size
# RUN pip install --no-cache-dir -r requirements.txt

# STEP 4: Copy application code
# COPY source destination
# First dot (.) = current directory on host machine (where Dockerfile is)
# Second dot (.) = current directory in container (/app)
# This copies all files and folders to the container
COPY . .

# STEP 5: Expose port (documentation only, doesn't actually publish)
# EXPOSE tells Docker that container listens on port 8000 at runtime
# This is informational - actual port mapping happens with "docker run -p"
EXPOSE 8000

# STEP 6: Define the command to run when container starts
# CMD provides default command for executing container
# Format: CMD ["executable", "param1", "param2"]
# uvicorn is ASGI server for running FastAPI applications
# main:app means "app" object in "main.py" file
# --host 0.0.0.0 makes server accessible from outside container
# --port 8000 specifies the port number
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Alternative for regular Python scripts:
# CMD ["python", "app.py"]

# =============================================================================
# DOCKER COMMANDS WORKFLOW
# =============================================================================

# BUILD THE IMAGE
# -t flag tags/names the image
# Syntax: docker build -t <image_name> <path_to_dockerfile_directory>

# If Dockerfile is in current directory:
# docker build -t myfastapiapp .

# If Dockerfile is in subdirectory:
# docker build -t myfastapiapp ./backend

# If Dockerfile has different name (e.g., Dockerfile.prod):
# docker build -t myfastapiapp -f Dockerfile.prod .

# RUN THE CONTAINER
# Syntax: docker run [OPTIONS] IMAGE_NAME
# -d flag runs container in detached mode (background)
# -p flag maps ports: -p <host_port>:<container_port>
# Left side = port on your local machine
# Right side = port inside container (matches EXPOSE)

# docker run -d -p 8000:8000 myfastapiapp

# Now access your FastAPI app at: http://localhost:8000
# API docs available at: http://localhost:8000/docs

# USEFUL DOCKER COMMANDS:
# docker ps                          # List running containers
# docker ps -a                       # List all containers (including stopped)
# docker images                      # List all images
# docker stop <container_id>         # Stop a running container
# docker rm <container_id>           # Remove a container
# docker rmi <image_id>              # Remove an image
# docker logs <container_id>         # View container logs
# docker exec -it <container_id> bash # Access container shell
# docker-compose up                  # Run multi-container apps (with docker-compose.yml)

# PORT MAPPING EXAMPLES:
# docker run -d -p 8080:8000 myfastapiapp   # Access on localhost:8080
# docker run -d -p 3000:8000 myfastapiapp   # Access on localhost:3000

# =============================================================================
# BEST PRACTICES
# =============================================================================

# 1. Use specific image versions (python:3.11-slim, not python:latest)
# 2. Order instructions from least to most frequently changing (leverage caching)
# 3. Combine RUN commands to reduce layers: RUN apt-get update && apt-get install -y
# 4. Use .dockerignore file to exclude unnecessary files (like .git, __pycache__)
# 5. Don't run containers as root user (add USER instruction)
# 6. Keep images small (use slim/alpine variants, multi-stage builds)
# 7. One process per container (don't run multiple services in one container)
# 8. Use environment variables for configuration (ENV instruction)
# 9. Always specify --host 0.0.0.0 in CMD for network accessibility