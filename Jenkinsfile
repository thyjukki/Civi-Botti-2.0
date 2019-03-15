/* Requires the Docker Pipeline plugin */
node('virtualenv&&python3') {
    checkout scm

    withPythonEnv('python3') {
        stage('Build') {
            sh 'pip install -r requirements.txt'
        }
        stage('UnitTest') {
            sh 'python -m unittest discover ./tests'
        }
    }
}