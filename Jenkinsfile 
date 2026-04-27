pipeline {
  agent any
  stages {
    stage('Sanity') {
      steps {
        echo "Jenkinsfile loaded from SCM successfully"
        sh 'pwd'
        sh 'ls -la'
      }
    }
  }
}