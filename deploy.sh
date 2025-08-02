#!/bin/bash

set -e  # Exit on any error
set -o pipefail

echo "🚀 Starting deployment at $(date)"

# Configuration
PROJECT_DIR="/opt/software_portal"
VENV_DIR="$PROJECT_DIR/venv"
SERVICE_NAME="software_portal.service"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if service exists
service_exists() {
    systemctl list-unit-files | grep -q "^$1"
}

# Navigate to project directory
cd "$PROJECT_DIR" || { echo "❌ Failed to cd into $PROJECT_DIR"; exit 1; }

echo "🔄 Git repository status..."
git status --porcelain

echo "🐍 Activating virtual environment..."
if [ ! -d "$VENV_DIR" ]; then
    echo "⚠️ Virtual environment not found. Creating one..."
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"

echo "📦 Installing/updating dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🔧 Running Django checks..."
python manage.py check --deploy

echo "🛠️ Running database migrations..."
python manage.py migrate --noinput

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "🧹 Cleaning up Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

echo "♻️ Restarting services..."
if service_exists "$SERVICE_NAME"; then
    sudo systemctl restart "$SERVICE_NAME"
    sudo systemctl status "$SERVICE_NAME" --no-pager -l
else
    echo "⚠️ Service $SERVICE_NAME not found. Please set up the service first."
fi

# Restart nginx if it exists
if command_exists nginx && service_exists "nginx.service"; then
    echo "🔄 Reloading nginx configuration..."
    sudo nginx -t && sudo systemctl reload nginx
fi

echo "🔍 Final health check..."
sleep 5
if service_exists "$SERVICE_NAME"; then
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo "✅ Service is running successfully"
    else
        echo "❌ Service failed to start"
        sudo systemctl status "$SERVICE_NAME" --no-pager -l
        exit 1
    fi
fi

echo "✅ Deployment complete at $(date)"
echo "🌐 Application should be available at your configured domain"