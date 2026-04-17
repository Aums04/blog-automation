pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = '1'
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
                echo '=== Stage 1: Installing Dependencies ==='
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                echo '=== Stage 2: Running Test Suite ==='
                sh 'python -m pytest test_blog.py -v --tb=short --junitxml=test-results.xml || python -m unittest test_blog -v 2>&1 | tee test-output.txt'
            }
        }

        stage('Generate Blog Content') {
            steps {
                echo '=== Stage 3: Generating Blog Content via Gemini AI ==='
                script {
                    if (params.DIRECT_PUBLISH) {
                        echo 'Mode: DIRECT PUBLISH (auto)'
                        sh "python generate_blog.py --topic \"${params.BLOG_TOPIC}\" --direct-publish"
                    } else {
                        echo 'Mode: MANUAL APPROVAL'
                        sh "python generate_blog.py --topic \"${params.BLOG_TOPIC}\""
                    }
                }
                // Show preview in Jenkins console log
                script {
                    def title = readFile('blog_title.txt').trim()
                    def content = readFile('blog_content.txt').trim()
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
                echo '=== Stage 5: Publishing to Medium via Selenium ==='
                echo 'Selenium will: Login (via Chrome profile) -> Write Story -> Type Content -> Publish'
                sh 'python publish_blog.py'
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
            echo 'Blog post has been published to Medium.'
        }
        failure {
            echo 'RESULT: Pipeline FAILED. Check stage logs for details.'
        }
    }
}
