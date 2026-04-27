pipeline {
    agent any

    environment {
        PYTHONPATH = "${WORKSPACE}"
    }

    stages {

        stage('Checkout') {
            steps {
                echo '📥 Checking out code...'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo '📦 Installing Python dependencies...'
                sh '''
                    apt-get update && apt-get install -y python3 python3-pip
                    python3 -m pip install --upgrade pip
                    pip3 install -r requirements.txt
                '''
            }
        }

        stage('Kafka Health Check') {
            steps {
                echo '🔍 Checking Kafka is reachable...'
                sh '''
                    python3 -c "
from kafka import KafkaAdminClient
client = KafkaAdminClient(bootstrap_servers='localhost:9092')
print('Kafka brokers:', client.describe_cluster())
client.close()
"
                '''
            }
        }

        stage('Produce Test Events') {
            steps {
                echo '📨 Sending test events to Kafka...'
                sh 'python3 producer/produ.py'
            }
        }

        stage('Run Kafka Tests') {
            steps {
                echo '🧪 Running Kafka QA tests...'
                sh 'pytest tests/test_kafka.py -v --tb=short'
            }
        }

        stage('Run Spark Unit Tests') {
            steps {
                echo '⚡ Running Spark transformation tests...'
                sh 'pytest tests/test_spark.py -v --tb=short'
            }
        }

        stage('Run Data Quality Tests') {
            steps {
                echo '✅ Running data quality checks...'
                sh 'pytest tests/test_data_quality.py -v --tb=short'
            }
        }

        stage('Generate Test Report') {
            steps {
                sh 'pytest tests/ --html=report.html --self-contained-html || true'
            }
            post {
                always {
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: '.',
                        reportFiles: 'report.html',
                        reportName: 'QA Test Report'
                    ])
                }
            }
        }
    }

    post {
        success {
            echo '🎉 All pipeline tests passed!'
        }
        failure {
            echo '❌ Pipeline failed — check test report!'
        }
    }
}