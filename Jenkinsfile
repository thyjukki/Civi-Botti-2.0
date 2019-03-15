/* Requires the Docker Pipeline plugin */
node('virtualenv&&python3') {
    checkout scm
    stage('Build') {
        sh 'virtualenv venv -p python3'
        sh 'source ./venv/bin/activate'
        sh 'pip install -r requirements.txt'
    }
    stage('UnitTest') {
        sh 'python -m unittest discover ./tests'
    }
}