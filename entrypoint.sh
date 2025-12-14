#!/bin/sh
set -e # Exit immediately if any command returns a non-zero status

# Check for environment variables
if [ -z "${PI_HOST}" ] || [ -z "${PI_USER}" ] || [ -z "${PI_PASS}" ]; then
    echo "Error: PI_HOST, PI_USER, and PI_PASS environment variables must be set." >&2
    exit 1
fi

REMOTE_APP_PATH="/home/${PI_USER}/hw_display/app"
SSH_OPTS="-o StrictHostKeyChecking=no"

# 1. Create directory
echo "Creating remote directory..."
sshpass -p "${PI_PASS}" ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "mkdir -p ${REMOTE_APP_PATH}"

# 2. Copy files
echo "Copying application to the device..."
sshpass -p "${PI_PASS}" scp $SSH_OPTS -r ./app/* "${PI_USER}@${PI_HOST}:${REMOTE_APP_PATH}/"

# 3. Install dependencies
echo "Installing dependencies on the device..."
sshpass -p "${PI_PASS}" ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "pip3 install -r ${REMOTE_APP_PATH}/requirements.txt --break-system-packages"

# 4. Start application
echo "Starting application on the device..."
sshpass -p "${PI_PASS}" ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "python3 ${REMOTE_APP_PATH}/main.py"