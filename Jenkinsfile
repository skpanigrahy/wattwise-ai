pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'your-registry.com'
        IMAGE_TAG = "${BUILD_NUMBER}"
        BACKEND_IMAGE = "${DOCKER_REGISTRY}/wattwise-backend:${IMAGE_TAG}"
        FRONTEND_IMAGE = "${DOCKER_REGISTRY}/wattwise-frontend:${IMAGE_TAG}"
        DEPLOY_HOST = 'your-deploy-server.com'
        DEPLOY_USER = 'deploy'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
            }
        }
        
        stage('Setup Environment') {
            steps {
                echo 'Setting up environment...'
                sh '''
                    # Create .env files from examples
                    cp backend/.env.example backend/.env
                    cp frontend/.env.example frontend/.env
                    
                    # Install dependencies for testing
                    cd backend && pip install -r requirements.txt
                    cd ../tests && pip install -r requirements.txt
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Running tests...'
                sh '''
                    cd tests
                    python run_tests.py --type all --no-coverage
                '''
            }
            post {
                always {
                    // Publish test results
                    publishTestResults testResultsPattern: 'tests/test-results.xml'
                    
                    // Archive test artifacts
                    archiveArtifacts artifacts: 'tests/htmlcov/**', allowEmptyArchive: true
                }
            }
        }
        
        stage('Build Backend Image') {
            steps {
                echo 'Building backend Docker image...'
                script {
                    def backendImage = docker.build("${BACKEND_IMAGE}", "./backend")
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'docker-registry-credentials') {
                        backendImage.push()
                        backendImage.push("latest")
                    }
                }
            }
        }
        
        stage('Build Frontend Image') {
            steps {
                echo 'Building frontend Docker image...'
                script {
                    def frontendImage = docker.build("${FRONTEND_IMAGE}", "./frontend")
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'docker-registry-credentials') {
                        frontendImage.push()
                        frontendImage.push("latest")
                    }
                }
            }
        }
        
        stage('Security Scan') {
            steps {
                echo 'Running security scans...'
                sh '''
                    # Run Trivy security scan on images
                    trivy image --exit-code 0 --severity HIGH,CRITICAL ${BACKEND_IMAGE} || true
                    trivy image --exit-code 0 --severity HIGH,CRITICAL ${FRONTEND_IMAGE} || true
                '''
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                echo 'Deploying to staging environment...'
                sh '''
                    # Deploy to staging using SSH
                    ssh ${DEPLOY_USER}@${DEPLOY_HOST} "
                        cd /opt/wattwise-staging &&
                        git pull origin develop &&
                        docker-compose down &&
                        docker-compose pull &&
                        docker-compose up -d
                    "
                '''
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying to production environment...'
                input message: 'Deploy to production?', ok: 'Deploy'
                
                sh '''
                    # Deploy to production using the deployment script
                    ./deploy/deploy_ssh.sh production
                '''
            }
        }
        
        stage('Health Check') {
            steps {
                echo 'Performing health checks...'
                sh '''
                    # Wait for services to be ready
                    sleep 30
                    
                    # Check backend health
                    curl -f http://${DEPLOY_HOST}:8000/health || exit 1
                    
                    # Check frontend health
                    curl -f http://${DEPLOY_HOST}:8501/_stcore/health || exit 1
                    
                    echo "All health checks passed!"
                '''
            }
        }
    }
    
    post {
        always {
            echo 'Cleaning up...'
            sh 'docker system prune -f'
        }
        
        success {
            echo 'Pipeline completed successfully!'
            slackSend(
                channel: '#deployments',
                color: 'good',
                message: "✅ WattWise AI deployment successful - Build #${BUILD_NUMBER}"
            )
        }
        
        failure {
            echo 'Pipeline failed!'
            slackSend(
                channel: '#deployments',
                color: 'danger',
                message: "❌ WattWise AI deployment failed - Build #${BUILD_NUMBER}"
            )
        }
    }
}

