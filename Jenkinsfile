pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = '1'
        // Define VENV path for consistency
        VENV_PATH = 'venv'
        PYTHON_EXE = "${isUnix() ? 'venv/bin/python' : 'venv\\Scripts\\python.exe'}"
    }

    parameters {
        booleanParam(name: 'RANDOM_TOPIC', defaultValue: true, description: 'Let AI suggest a trending topic automatically.')
        string(name: 'BLOG_TOPIC', defaultValue: 'The Future of AI in Software Testing', description: 'Manual topic (ignored if RANDOM_TOPIC is checked).')
        booleanParam(name: 'DIRECT_PUBLISH', defaultValue: false, description: 'Skip manual approval and publish immediately.')
    }

    triggers {
        // Scheduled daily posting at 8 AM - Defaults to RANDOM topics
        cron('H 8 * * *')
    }

    stages {
        stage('Setup') {
            steps {
                echo '=== Stage 1: Setting up Virtual Environment ==='
                script {
                    if (isUnix()) {
                        sh 'python3 -m venv ${VENV_PATH} || python -m venv ${VENV_PATH}'
                        sh "${VENV_PATH}/bin/pip install -r requirements.txt"
                    } else {
                        bat "python -m venv ${VENV_PATH}"
                        bat "${VENV_PATH}\\Scripts\\pip install -r requirements.txt"
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                echo '=== Stage 2: Running Test Suite ==='
                script {
                    if (isUnix()) {
                        sh "${PYTHON_EXE} -m pytest tests/test_blog.py"
                    } else {
                        bat "${PYTHON_EXE} -m pytest tests/test_blog.py"
                    }
                }
            }
        }

        stage('Generate Blog Content') {
            steps {
                echo '=== Stage 3: Generating Blog Content via Gemini AI ==='
                withCredentials([string(credentialsId: 'GEMINI_API_KEY_SECRET', variable: 'GEMINI_API_KEY')]) {
                    script {
                        def publishFlag = params.DIRECT_PUBLISH ? "--direct-publish" : ""
                        def randomFlag = params.RANDOM_TOPIC ? "--random-topic" : ""
                        def topicArg = params.RANDOM_TOPIC ? "" : "--topic \"${params.BLOG_TOPIC}\""
                        
                        if (isUnix()) {
                            sh "export GEMINI_API_KEY=${GEMINI_API_KEY} && ${PYTHON_EXE} src/generate_blog.py ${topicArg} ${randomFlag} ${publishFlag}"
                        } else {
                            bat "set GEMINI_API_KEY=${GEMINI_API_KEY} && ${PYTHON_EXE} src/generate_blog.py ${topicArg} ${randomFlag} ${publishFlag}"
                        }
                    }
                }
                
                // Show preview in Jenkins console log
                script {
                    def title = readFile('data/blog_title.txt').trim()
                    def content = readFile('data/blog_content.txt').trim()
                    echo "=========== BLOG PREVIEW ==========="
                    echo "Title: ${title}"
                    echo "Content (first 500 chars):"
                    echo "${content.take(500)}..."
                    echo "====================================="
                }
            }
        }

        stage('Manual Approval') {
            when {
                expression { return !params.DIRECT_PUBLISH }
            }
            steps {
                echo '=== Stage 4: Awaiting Manual Approval ==='
                input message: 'Review the generated blog post in the console log above. Approve to publish?', ok: 'Approve & Publish'
            }
        }

        stage('Publish via Selenium') {
            steps {
                echo '=== Stage 5: Publishing to Dev.to via Selenium ==='
                echo 'Selenium will: Login (via Profile or Credentials) -> New Post -> Type Title + Content -> Publish'
                withCredentials([
                    string(credentialsId: 'DEVTO_EMAIL_SECRET', variable: 'DEVTO_EMAIL'),
                    string(credentialsId: 'DEVTO_PASSWORD_SECRET', variable: 'DEVTO_PASSWORD')
                ]) {
                    script {
                        if (isUnix()) {
                            sh "export DEVTO_EMAIL=${DEVTO_EMAIL} && export DEVTO_PASSWORD=${DEVTO_PASSWORD} && ${PYTHON_EXE} src/publish_blog.py"
                        } else {
                            bat "set DEVTO_EMAIL=${DEVTO_EMAIL} && set DEVTO_PASSWORD=${DEVTO_PASSWORD} && ${PYTHON_EXE} src/publish_blog.py"
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            echo '========================================='
            echo '         PIPELINE EXECUTION REPORT       '
            echo '========================================='
            echo "Mode: ${params.RANDOM_TOPIC ? 'Random AI Topic' : 'Manual Topic'}"
            if (!params.RANDOM_TOPIC) { echo "Topic: ${params.BLOG_TOPIC}" }
            echo "Direct Publish: ${params.DIRECT_PUBLISH}"
            echo "Timestamp: ${new Date()}"
            echo '========================================='
        }
        success {
            echo 'RESULT: Pipeline completed SUCCESSFULLY.'
            echo 'Blog post has been published to Dev.to.'
        }
        failure {
            echo 'RESULT: Pipeline FAILED. Check stage logs for details.'
        }
    }
}
