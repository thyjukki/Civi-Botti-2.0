/* Requires the Docker Pipeline plugin */
node('virtualenv&&python3') {
    checkout scm

    withPythonEnv('python3') {
        stage('Build') {
            sh 'pip install -r requirements.txt'
        }
        stage('Lint') {
            sh 'pycodestyle civbot'
        }
        stage('UnitTest') {
            sh 'python -m unittest discover ./tests'
        }
        stage('UnitTest') {
            sh 'python -m unittest discover ./tests'
        }
        if (env.BRANCH_NAME == 'master') {
            stage('UnitTest') {
                build 'civi-botti-deploy'
            }
        }
    }
}