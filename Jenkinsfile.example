pipeline{
    environment{
        APP_NAME = "BHH-example"
        IMAGE_TAG = "registry.example.com/${APP_NAME}:${env.BRANCH_NAME}.${env.BUILD_NUMBER}"
        GIT_URI = "http://github.com/jacky9813/bhh.git"
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