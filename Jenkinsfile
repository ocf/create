def version

pipeline {
  // TODO: Make this cleaner: https://issues.jenkins-ci.org/browse/JENKINS-42643
  triggers {
    upstream(
      upstreamProjects: (env.BRANCH_NAME == 'master' ? 'ocflib/master,dockers/master' : ''),
      threshold: hudson.model.Result.SUCCESS,
    )
  }

  agent {
    label 'slave'
  }

  options {
    ansiColor('xterm')
    timeout(time: 1, unit: 'HOURS')
    timestamps()
  }

  stages {
    stage('check-gh-trust') {
      steps {
        checkGitHubAccess()

        script {
          version = new Date().format("yyyy-MM-dd-'T'HH-mm-ss")
        }
      }
    }

    stage('parallel-test-cook') {
      environment {
        DOCKER_REVISION = "${version}"
      }
      parallel {
        stage('test') {
          steps {
            sh 'make test'
          }
        }

        stage('cook-image') {
          steps {
            sh 'make cook-image'
          }
        }
      }
    }

    stage('push-to-registry') {
      environment {
        DOCKER_REVISION = "${version}"
      }
      when {
        branch 'master'
      }
      agent {
        label 'deploy'
      }
      steps {
        sh 'make push-image'
      }
    }

    stage('deploy-to-prod') {
      when {
        branch 'master'
      }
      agent {
        label 'deploy'
      }
      steps {
        // TODO: Make these deploy and roll back together! (make it atomic)
        // TODO: Also try to parallelize these if possible?
        marathonDeployApp('create/worker', version)
        marathonDeployApp('create/healthcheck', version)
      }
    }
  }

  post {
    failure {
      emailNotification()
    }
    always {
      node(label: 'slave') {
        ircNotification()
      }
    }
  }
}

// vim: ft=groovy
