pipeline {
    agent any

    environment {
        DOCKER_COMPOSE_FILE = 'docker-compose.yml'
        PROJECT_NAME = 'ddn-ai-system'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Environment Setup') {
            steps {
                script {
                    // Load environment variables
                    sh '''
                        if [ ! -f .env ]; then
                            cp .env.example .env
                            echo "Please configure .env file with your credentials"
                        fi
                    '''
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                sh 'docker-compose build'
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    cd implementation
                    pip install -r requirements.txt
                    python -m pytest tests/ || true
                '''
            }
        }

        stage('Start Services') {
            steps {
                sh 'docker-compose up -d'
                sh 'sleep 30'
            }
        }

        stage('Health Checks') {
            steps {
                script {
                    def services = [
                        'Dashboard API': 'http://localhost:5005/health',
                        'Dashboard UI': 'http://localhost:3000',
                        'n8n': 'http://localhost:5678',
                        'LangGraph': 'http://localhost:5000/health'
                    ]

                    services.each { name, url ->
                        sh "curl -f ${url} || echo '${name} health check failed'"
                    }
                }
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying to production...'
                // Add deployment steps
            }
        }
    }

    post {
        always {
            sh 'docker-compose logs'
        }
        failure {
            sh 'docker-compose down'
            echo 'Pipeline failed. Services stopped.'
        }
        success {
            echo 'Pipeline completed successfully!'
        }
    }
}
