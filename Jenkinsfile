pipeline {
    agent any

    stages {

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t crop-app .'
            }
        }

        stage('Stop Old Container') {
            steps {
                bat 'docker stop crop-container || exit 0'
                bat 'docker rm crop-container || exit 0'
            }
        }

        stage('Run Container') {
            steps {
                bat 'docker run -d -p 5000:5000 --name crop-container crop-app'
            }
        }
    }
}