pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = '1'
        // Define VENV path for consistency
        VENV_PATH = 'venv'
        PYTHON_EXE = "${isUnix() ? 'venv/bin/python' : 'venv\\Scripts\\python.exe'}"
    }

    parameters {
        booleanParam(name: 'DIRECT_PUBLISH', defaultValue: false, description: 'Skip manual approval and publish immediately.')
        string(name: 'BLOG_TOPIC', defaultValue: 'The Future of AI in Software Testing', description: 'Topic for Gemini to write about.')
    }

    triggers {
        // Scheduled daily posting at 8 AM
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
                        sh "${PYTHON_EXE} tests/test_blog.py"
                    } else {
                        bat "${PYTHON_EXE} tests/test_blog.py"
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
                        if (isUnix()) {
                            sh "export GEMINI_API_KEY=${GEMINI_API_KEY} && ${PYTHON_EXE} src/generate_blog.py --topic \"${params.BLOG_TOPIC}\" ${publishFlag}"
                        } else {
                            bat "set GEMINI_API_KEY=${GEMINI_API_KEY} && ${PYTHON_EXE} src/generate_blog.py --topic \"${params.BLOG_TOPIC}\" ${publishFlag}"
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
                echo 'Selenium will: Login (via Chrome profile) -> New Post -> Type Title + Content -> Publish'
                script {
                    if (isUnix()) {
                        sh "${PYTHON_EXE} src/publish_blog.py"
                    } else {
                        bat "${PYTHON_EXE} src/publish_blog.py"
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
            echo "Topic: ${params.BLOG_TOPIC}"
            echo "Mode: ${params.DIRECT_PUBLISH ? 'Direct Publish (Automated)' : 'Manual Approval'}"
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
