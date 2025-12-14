FROM python:3.14-slim

ARG SSH_HOST
ARG SSH_USER
ARG SSH_PASS

# Prevent interactive prompts during apt installation
ENV DEBIAN_FRONTEND=noninteractive

# Install sshpass and openssh-client
RUN apt-get update && apt-get install -y --no-install-recommends \
    sshpass \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# Copy the entrypoint script and make it executable
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Copy the application source code
# Assuming your folder structure is local_folder/app -> remote_container/app
COPY ./app ./app

# Set defaults (Can be overridden at runtime)
ENV PI_HOST=${SSH_HOST}
ENV PI_USER=${SSH_USER}
ENV PI_PASS=${SSH_PASS}

# Run the shell script
CMD ["./entrypoint.sh"]