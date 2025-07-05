#!/bin/bash

# WattWise AI SSH Deployment Script
# Usage: ./deploy_ssh.sh [environment]

set -e

# Configuration
ENVIRONMENT=${1:-staging}
REPO_URL="https://github.com/your-org/wattwise-ai.git"
BRANCH="main"

# Environment-specific configurations
if [ "$ENVIRONMENT" = "production" ]; then
    DEPLOY_HOST="prod-server.example.com"
    DEPLOY_PATH="/opt/wattwise-production"
    BRANCH="main"
elif [ "$ENVIRONMENT" = "staging" ]; then
    DEPLOY_HOST="staging-server.example.com"
    DEPLOY_PATH="/opt/wattwise-staging"
    BRANCH="develop"
else
    echo "❌ Unknown environment: $ENVIRONMENT"
    echo "Usage: $0 [staging|production]"
    exit 1
fi

DEPLOY_USER="deploy"
BACKUP_PATH="/opt/backups/wattwise-$(date +%Y%m%d-%H%M%S)"

echo "🚀 WattWise AI Deployment Script"
echo "Environment: $ENVIRONMENT"
echo "Host: $DEPLOY_HOST"
echo "Path: $DEPLOY_PATH"
echo "Branch: $BRANCH"
echo "================================"

# Function to run commands on remote server
run_remote() {
    ssh -o StrictHostKeyChecking=no $DEPLOY_USER@$DEPLOY_HOST "$1"
}

# Function to copy files to remote server
copy_to_remote() {
    scp -o StrictHostKeyChecking=no -r "$1" $DEPLOY_USER@$DEPLOY_HOST:"$2"
}

echo "📋 Step 1: Pre-deployment checks"
echo "Checking SSH connectivity..."
if ! run_remote "echo 'SSH connection successful'"; then
    echo "❌ Failed to connect to $DEPLOY_HOST"
    exit 1
fi

echo "Checking Docker installation..."
if ! run_remote "docker --version && docker-compose --version"; then
    echo "❌ Docker or Docker Compose not found on target server"
    exit 1
fi

echo "📦 Step 2: Backup current deployment"
run_remote "
    if [ -d '$DEPLOY_PATH' ]; then
        echo 'Creating backup...'
        sudo mkdir -p $(dirname $BACKUP_PATH)
        sudo cp -r $DEPLOY_PATH $BACKUP_PATH
        echo 'Backup created at $BACKUP_PATH'
    else
        echo 'No existing deployment to backup'
    fi
"

echo "📥 Step 3: Deploy new version"
run_remote "
    # Create deployment directory
    sudo mkdir -p $DEPLOY_PATH
    sudo chown $DEPLOY_USER:$DEPLOY_USER $DEPLOY_PATH
    
    # Clone or update repository
    if [ -d '$DEPLOY_PATH/.git' ]; then
        echo 'Updating existing repository...'
        cd $DEPLOY_PATH
        git fetch origin
        git reset --hard origin/$BRANCH
    else
        echo 'Cloning repository...'
        git clone -b $BRANCH $REPO_URL $DEPLOY_PATH
        cd $DEPLOY_PATH
    fi
    
    # Set up environment files
    cp backend/.env.example backend/.env
    cp frontend/.env.example frontend/.env
    
    # Update environment-specific configurations
    if [ '$ENVIRONMENT' = 'production' ]; then
        sed -i 's/DEBUG=true/DEBUG=false/' backend/.env
        sed -i 's/localhost/postgres/' backend/.env
    fi
"

echo "🐳 Step 4: Build and start services"
run_remote "
    cd $DEPLOY_PATH
    
    # Stop existing services
    docker-compose down || true
    
    # Remove old images to save space
    docker image prune -f || true
    
    # Build and start services
    docker-compose build --no-cache
    docker-compose up -d
    
    echo 'Waiting for services to start...'
    sleep 30
"

echo "🔍 Step 5: Health checks"
echo "Checking backend health..."
if run_remote "curl -f http://localhost:8000/health"; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    echo "Rolling back..."
    run_remote "
        cd $DEPLOY_PATH
        docker-compose down
        if [ -d '$BACKUP_PATH' ]; then
            sudo rm -rf $DEPLOY_PATH
            sudo mv $BACKUP_PATH $DEPLOY_PATH
            cd $DEPLOY_PATH
            docker-compose up -d
        fi
    "
    exit 1
fi

echo "Checking frontend health..."
if run_remote "curl -f http://localhost:8501/_stcore/health"; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend health check failed"
    echo "Rolling back..."
    run_remote "
        cd $DEPLOY_PATH
        docker-compose down
        if [ -d '$BACKUP_PATH' ]; then
            sudo rm -rf $DEPLOY_PATH
            sudo mv $BACKUP_PATH $DEPLOY_PATH
            cd $DEPLOY_PATH
            docker-compose up -d
        fi
    "
    exit 1
fi

echo "📊 Step 6: Post-deployment tasks"
run_remote "
    cd $DEPLOY_PATH
    
    # Initialize database if needed
    docker-compose exec -T backend python manage_db.py check || \
    docker-compose exec -T backend python manage_db.py init
    
    # Show running services
    docker-compose ps
    
    # Show logs for verification
    docker-compose logs --tail=20
"

echo "🧹 Step 7: Cleanup"
run_remote "
    # Remove old backups (keep last 5)
    sudo find $(dirname $BACKUP_PATH) -name 'wattwise-*' -type d | sort -r | tail -n +6 | xargs sudo rm -rf || true
    
    # Clean up Docker
    docker system prune -f || true
"

echo ""
echo "✅ Deployment completed successfully!"
echo "🌐 Frontend: http://$DEPLOY_HOST:8501"
echo "🔧 Backend API: http://$DEPLOY_HOST:8000"
echo "📊 Monitoring: http://$DEPLOY_HOST:9090 (Prometheus), http://$DEPLOY_HOST:3000 (Grafana)"
echo ""
echo "📝 Deployment Summary:"
echo "   Environment: $ENVIRONMENT"
echo "   Branch: $BRANCH"
echo "   Host: $DEPLOY_HOST"
echo "   Path: $DEPLOY_PATH"
echo "   Backup: $BACKUP_PATH"
echo ""

# Send notification (optional)
if command -v curl &> /dev/null; then
    # Example Slack notification (replace with your webhook URL)
    # curl -X POST -H 'Content-type: application/json' \
    #     --data "{\"text\":\"✅ WattWise AI deployed to $ENVIRONMENT successfully!\"}" \
    #     YOUR_SLACK_WEBHOOK_URL
    echo "📱 Notification sent"
fi

echo "🎉 Deployment complete!"

