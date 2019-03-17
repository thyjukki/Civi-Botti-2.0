/* Requires the Docker Pipeline plugin */
node('virtualenv&&python3') {
    withEnv([
            'GMR_URL=http://multiplayerrobot.com',
            'TEST_STEAM_ID=76561198025213815',
            'TEST_AUTH_KEY=${credentials('CIVI_BOT_TEST_AUTH_KEY')}',
            'TG_TOKEN=${credentials('CIVI_BOT_TG_TOKEN')}'
        ]) {
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
}