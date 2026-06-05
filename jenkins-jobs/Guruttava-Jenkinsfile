// Jenkinsfile for Guruttava Mobile & Web Test Automation
// Supports: Android, iOS, and Web testing using Robot Framework
// Multi-Project Architecture Integration

pipeline {
    agent any

    environment {
        // Project Context (CRITICAL for multi-project isolation)
        PROJECT_SLUG = 'guruttava'
        PROJECT_ID = '2'  // Guruttava project ID from database

        // Test Configuration
        APPIUM_SERVER = 'http://localhost:4723'
        ROBOT_OPTIONS = '--outputdir results'

        // Python Workflow API (Manual Trigger Service)
        TRIGGER_API_URL = 'http://host.docker.internal:5004'

        // Build metadata
        BUILD_TIMESTAMP = sh(script: 'date +%Y%m%d_%H%M%S', returnStdout: true).trim()
    }

    parameters {
        choice(
            name: 'PLATFORM',
            choices: ['All', 'Android', 'iOS', 'Web'],
            description: 'Select platform to test'
        )
        choice(
            name: 'TEST_TYPE',
            choices: ['All', 'Smoke', 'Regression', 'Sanity'],
            description: 'Select test type'
        )
        string(
            name: 'DEVICE_NAME',
            defaultValue: 'emulator-5554',
            description: 'Android device name or iOS simulator'
        )
        string(
            name: 'APP_PATH',
            defaultValue: 'apps/guruttava.apk',
            description: 'Path to mobile app (APK/APP file)'
        )
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    echo "📥 Checking out Guruttava test repository"
                }
                git branch: 'main',
                    url: 'https://github.com/Guruttava-Org/guruttava-automation.git'
            }
        }

        stage('Setup Environment') {
            steps {
                script {
                    echo "🔧 Setting up Python environment and dependencies"
                }
                sh '''
                    # Create virtual environment
                    python3 -m venv venv || python -m venv venv

                    # Activate virtual environment
                    . venv/bin/activate || . venv/Scripts/activate

                    # Upgrade pip
                    python -m pip install --upgrade pip

                    # Install dependencies
                    pip install -r requirements.txt

                    # Install Robot Framework and Appium
                    pip install robotframework robotframework-appiumlibrary
                    pip install robotframework-seleniumlibrary
                    pip install robotframework-requests

                    # Verify installations
                    robot --version
                    python --version
                '''
            }
        }

        stage('Verify Appium') {
            when {
                expression {
                    params.PLATFORM in ['Android', 'iOS', 'All']
                }
            }
            steps {
                script {
                    echo "📱 Verifying Appium server connection"
                }
                sh '''
                    # Check if Appium server is accessible
                    curl -f ${APPIUM_SERVER}/wd/hub/status || {
                        echo "⚠️  Appium server not accessible at ${APPIUM_SERVER}"
                        echo "Please ensure Appium server is running"
                        exit 1
                    }
                '''
            }
        }

        stage('Run Tests - Android') {
            when {
                expression {
                    params.PLATFORM == 'Android' || params.PLATFORM == 'All'
                }
            }
            steps {
                script {
                    echo "🤖 Running Android tests"
                }
                sh '''
                    . venv/bin/activate || . venv/Scripts/activate

                    robot --variable PLATFORM:Android \\
                          --variable DEVICE_NAME:${DEVICE_NAME} \\
                          --variable APP_PATH:${APP_PATH} \\
                          --variable APPIUM_SERVER:${APPIUM_SERVER} \\
                          --variable TEST_TYPE:${TEST_TYPE} \\
                          ${ROBOT_OPTIONS} \\
                          tests/mobile/android/ || true
                '''
            }
        }

        stage('Run Tests - iOS') {
            when {
                expression {
                    params.PLATFORM == 'iOS' || params.PLATFORM == 'All'
                }
            }
            steps {
                script {
                    echo "🍎 Running iOS tests"
                }
                sh '''
                    . venv/bin/activate || . venv/Scripts/activate

                    robot --variable PLATFORM:iOS \\
                          --variable DEVICE_NAME:${DEVICE_NAME} \\
                          --variable APP_PATH:${APP_PATH} \\
                          --variable APPIUM_SERVER:${APPIUM_SERVER} \\
                          --variable TEST_TYPE:${TEST_TYPE} \\
                          ${ROBOT_OPTIONS} \\
                          tests/mobile/ios/ || true
                '''
            }
        }

        stage('Run Tests - Web') {
            when {
                expression {
                    params.PLATFORM == 'Web' || params.PLATFORM == 'All'
                }
            }
            steps {
                script {
                    echo "🌐 Running Web tests"
                }
                sh '''
                    . venv/bin/activate || . venv/Scripts/activate

                    robot --variable BROWSER:Chrome \\
                          --variable TEST_TYPE:${TEST_TYPE} \\
                          ${ROBOT_OPTIONS} \\
                          tests/web/ || true
                '''
            }
        }

        stage('Parse Results') {
            steps {
                script {
                    echo "📊 Parsing Robot Framework test results"

                    // Parse output.xml to extract test statistics
                    def outputXml = readFile('results/output.xml')

                    // Use Python to parse XML and extract stats
                    sh '''
                        . venv/bin/activate || . venv/Scripts/activate

                        python3 << 'PYTHON_SCRIPT'
import xml.etree.ElementTree as ET
import sys

try:
    tree = ET.parse('results/output.xml')
    root = tree.getroot()

    stats = root.find('.//statistics/total/stat')
    if stats is not None:
        passed = int(stats.get('pass', 0))
        failed = int(stats.get('fail', 0))
        total = passed + failed

        print(f"TOTAL_TESTS={total}")
        print(f"PASSED_TESTS={passed}")
        print(f"FAILED_TESTS={failed}")

        # Write to environment file for Jenkins
        with open('test_stats.txt', 'w') as f:
            f.write(f"TOTAL_TESTS={total}\\n")
            f.write(f"PASSED_TESTS={passed}\\n")
            f.write(f"FAILED_TESTS={failed}\\n")

        sys.exit(0 if failed == 0 else 1)
    else:
        print("ERROR: Could not parse statistics")
        sys.exit(1)

except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
PYTHON_SCRIPT
                    '''

                    // Load test statistics
                    def statsFile = readFile('test_stats.txt')
                    def stats = [:]
                    statsFile.split('\\n').each { line ->
                        if (line.contains('=')) {
                            def parts = line.split('=')
                            stats[parts[0]] = parts[1]
                        }
                    }

                    env.TOTAL_TESTS = stats['TOTAL_TESTS'] ?: '0'
                    env.PASSED_TESTS = stats['PASSED_TESTS'] ?: '0'
                    env.FAILED_TESTS = stats['FAILED_TESTS'] ?: '0'

                    echo "📊 Test Results: ${env.TOTAL_TESTS} total, ${env.PASSED_TESTS} passed, ${env.FAILED_TESTS} failed"
                }
            }
        }

        stage('Upload Results to Platform') {
            steps {
                script {
                    echo "📤 Uploading test results to DDN AI Platform"
                }
                sh '''
                    . venv/bin/activate || . venv/Scripts/activate

                    # Call robot_framework_parser.py to parse and upload results
                    python3 ${WORKSPACE}/../../implementation/robot_framework_parser.py \\
                        --output results/output.xml \\
                        --build-id ${BUILD_TAG} \\
                        --project-id ${PROJECT_ID} \\
                        --project-slug ${PROJECT_SLUG} \\
                        --platform ${PLATFORM} \\
                        --test-type ${TEST_TYPE} \\
                        --mongodb-uri "${MONGODB_URI}" \\
                        --api-url ${TRIGGER_API_URL}/api/trigger-analysis || {
                            echo "⚠️  Result upload failed - continuing anyway"
                        }
                '''
            }
        }
    }

    post {
        always {
            script {
                echo "📝 Publishing Robot Framework reports"

                // Publish Robot Framework reports
                robot outputPath: 'results',
                      reportFileName: 'report.html',
                      logFileName: 'log.html',
                      outputFileName: 'output.xml',
                      passThreshold: 80.0,
                      unstableThreshold: 70.0,
                      onlyCritical: false

                // Archive test artifacts
                archiveArtifacts artifacts: 'results/**/*', allowEmptyArchive: true

                // Trigger Python workflow API with PROJECT context
                if (currentBuild.result == 'FAILURE' || env.FAILED_TESTS?.toInteger() > 0) {
                    echo "❌ Tests failed - triggering Python workflow analysis"

                    def payload = [
                        project_slug: env.PROJECT_SLUG,
                        project_id: env.PROJECT_ID.toInteger(),
                        build_id: env.BUILD_TAG,
                        job_name: env.JOB_NAME,
                        build_number: env.BUILD_NUMBER.toInteger(),
                        status: "FAILURE",
                        total_tests: env.TOTAL_TESTS?.toInteger() ?: 0,
                        passed_tests: env.PASSED_TESTS?.toInteger() ?: 0,
                        failed_tests: env.FAILED_TESTS?.toInteger() ?: 0,
                        platform: params.PLATFORM ?: 'All',
                        test_type: params.TEST_TYPE ?: 'All',
                        timestamp: new Date().format("yyyy-MM-dd'T'HH:mm:ss'Z'"),
                        build_url: env.BUILD_URL,
                        robot_report_url: "${env.BUILD_URL}robot/report/report.html",
                        trigger_source: "jenkins",
                        triggered_by_user: env.BUILD_USER_ID ?: "jenkins"
                    ]

                    try {
                        def response = httpRequest(
                            url: "${env.TRIGGER_API_URL}/api/trigger-analysis",
                            httpMode: 'POST',
                            contentType: 'APPLICATION_JSON',
                            requestBody: groovy.json.JsonOutput.toJson(payload),
                            validResponseCodes: '200:299',
                            timeout: 60
                        )
                        echo "✅ Analysis triggered successfully"
                    } catch (Exception e) {
                        echo "⚠️  Failed to trigger analysis: ${e.message}"
                    }
                }
            }
        }

        success {
            echo "✅ All tests passed for Guruttava ${params.PLATFORM}!"
            // Send success notification (optional)
        }

        failure {
            echo "❌ Tests failed - Python workflow analysis will be triggered automatically"
            // Send failure notification (optional)
        }

        unstable {
            echo "⚠️  Tests unstable - some failures detected"
        }

        cleanup {
            // Cleanup temporary files
            sh 'rm -f test_stats.txt || true'
        }
    }
}
