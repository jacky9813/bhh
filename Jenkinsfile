pipeline{
    environment{
        APP_NAME = "BHH-template"
        IMAGE_TAG = "registry.home.lab/${APP_NAME}:${env.BRANCH_NAME}.${env.BUILD_NUMBER}"
        GIT_URI = "http://git.jackyccc.tw/jacky/bhh-template.git"
        GIT_BRANCH = "master"
    }
    agent{
        dockerfile true
    }
    stages{
        stage('Build'){
            steps {
                git([url: "$GIT_URI", branch: "$GIT_BRANCH"])
                def dockerImage = dokcer.build IMAGE_TAG
                dockerImage.push()
            }
        }
    }
}