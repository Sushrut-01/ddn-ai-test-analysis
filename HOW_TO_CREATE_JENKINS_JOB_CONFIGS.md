# 🔧 How to Create Jenkins Job Configuration Files

**Purpose**: Document the process for creating Jenkins job configuration files for future multi-project setups
**Pattern Used**: Based on successful DDN and Guruttava implementations

---

## 📋 Overview

### What We Did for Guruttava:

1. ✅ Analyzed working DDN job configuration
2. ✅ Replicated the pattern for Guruttava
3. ✅ Created XML configuration file
4. ✅ Injected into Jenkins
5. ✅ Verified job appears and works

This guide explains how to repeat this process for **any new project**.

---

## 🎯 Step-by-Step Process

### Step 1: Analyze Existing Working Job

**Example: Analyzing DDN-Basic-Tests**

```bash
# Connect to Jenkins container
docker exec -it ddn-jenkins bash

# Navigate to jobs directory
cd /var/jenkins_home/jobs

# List all jobs
ls -la

# View working job configuration
cat DDN-Basic-Tests/config.xml
```

**What to Look For:**

1. **Job Type**: `<project>` (Freestyle) vs `<flow-definition>` (Pipeline)
2. **Parameters**: `<hudson.model.ParametersDefinitionProperty>`
3. **Build Script**: `<builders><hudson.tasks.Shell><command>`
4. **Triggers**: `<hudson.triggers.TimerTrigger>`
5. **Post-build Actions**: `<publishers>`

---

### Step 2: Extract the Configuration Template

**Copy Working Config:**

```bash
# From inside Jenkins container
cat /var/jenkins_home/jobs/DDN-Basic-Tests/config.xml > /tmp/template.xml

# Or from host machine
docker exec ddn-jenkins cat /var/jenkins_home/jobs/DDN-Basic-Tests/config.xml > jenkins-job-template.xml
```

**Or Use This Generic Template:**

Save this as `jenkins-freestyle-job-template.xml`:

```xml
<?xml version='1.1' encoding='UTF-8'?>
<project>
  <actions/>
  <description>REPLACE_WITH_DESCRIPTION</description>
  <keepDependencies>false</keepDependencies>

  <!-- Build History Settings -->
  <properties>
    <jenkins.model.BuildDiscarderProperty>
      <strategy class="hudson.tasks.LogRotator">
        <daysToKeep>30</daysToKeep>
        <numToKeep>50</numToKeep>
        <artifactDaysToKeep>-1</artifactDaysToKeep>
        <artifactNumToKeep>-1</artifactNumToKeep>
        <removeLastBuild>false</removeLastBuild>
      </strategy>
    </jenkins.model.BuildDiscarderProperty>

    <!-- Parameters -->
    <hudson.model.ParametersDefinitionProperty>
      <parameterDefinitions>
        <!-- Add parameters here -->
        REPLACE_WITH_PARAMETERS
      </parameterDefinitions>
    </hudson.model.ParametersDefinitionProperty>
  </properties>

  <scm class="hudson.scm.NullSCM"/>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>

  <!-- Build Triggers -->
  <triggers>
    REPLACE_WITH_TRIGGERS
  </triggers>

  <concurrentBuild>false</concurrentBuild>

  <!-- Build Steps -->
  <builders>
    <hudson.tasks.Shell>
      <command>REPLACE_WITH_SHELL_SCRIPT</command>
      <configuredLocalRules/>
    </hudson.tasks.Shell>
  </builders>

  <!-- Post-Build Actions -->
  <publishers>
    REPLACE_WITH_PUBLISHERS
  </publishers>

  <buildWrappers/>
</project>
```

---

### Step 3: Define Your New Project Parameters

**Create a Project Configuration Document:**

Save as `new-project-config.txt`:

```ini
[PROJECT_INFO]
PROJECT_NAME=MyNewProject
PROJECT_SLUG=mynewproject
PROJECT_ID=3
DESCRIPTION=MyNewProject Test Automation - Robot Framework tests

[GIT]
REPO_URL=https://github.com/your-org/mynewproject-tests
BRANCH=main

[MONGODB]
COLLECTION=mynewproject_test_failures

[JIRA]
PROJECT_KEY=MNP

[PINECONE]
NAMESPACE=mynewproject

[PARAMETERS]
PARAM1_NAME=TEST_TYPE
PARAM1_TYPE=choice
PARAM1_CHOICES=Smoke,Regression,Sanity,All
PARAM1_DESCRIPTION=Select test type

PARAM2_NAME=ENVIRONMENT
PARAM2_TYPE=choice
PARAM2_CHOICES=Dev,QA,Staging,Production
PARAM2_DESCRIPTION=Select environment

PARAM3_NAME=SEND_NOTIFICATIONS
PARAM3_TYPE=boolean
PARAM3_DEFAULT=true
PARAM3_DESCRIPTION=Send notifications on completion

[BUILD_TRIGGERS]
SCHEDULE=H */6 * * *

[TEST_SUITES]
SMOKE=tests/smoke/
REGRESSION=tests/regression/
SANITY=tests/sanity/
ALL=tests/
```

---

### Step 4: Build Parameter Definitions

**For Each Parameter Type:**

#### A. Choice Parameter (Dropdown)

```xml
<hudson.model.ChoiceParameterDefinition>
  <name>TEST_TYPE</name>
  <description>Select test type</description>
  <choices class="java.util.Arrays$ArrayList">
    <a class="string-array">
      <string>Smoke</string>
      <string>Regression</string>
      <string>Sanity</string>
      <string>All</string>
    </a>
  </choices>
</hudson.model.ChoiceParameterDefinition>
```

#### B. Boolean Parameter (Checkbox)

```xml
<hudson.model.BooleanParameterDefinition>
  <name>SEND_NOTIFICATIONS</name>
  <description>Send notifications to Teams/Slack on failure</description>
  <defaultValue>true</defaultValue>
</hudson.model.BooleanParameterDefinition>
```

#### C. String Parameter (Text Input)

```xml
<hudson.model.StringParameterDefinition>
  <name>DEVICE_NAME</name>
  <description>Android device name or iOS simulator</description>
  <defaultValue>emulator-5554</defaultValue>
  <trim>true</trim>
</hudson.model.StringParameterDefinition>
```

---

### Step 5: Create the Shell Script

**Template for Multi-Project Shell Script:**

```bash
#!/bin/bash
echo "========================================="
echo "PROJECT_NAME Tests (Robot Framework)"
echo "Build: $BUILD_NUMBER"
echo "Job: $JOB_NAME"
echo "========================================="

# Project Configuration (CRITICAL for multi-project isolation)
export PROJECT_ID="PROJECT_ID_NUMBER"
export PROJECT_SLUG="project_slug"
echo "Project ID: $PROJECT_ID | Slug: $PROJECT_SLUG"

# Git checkout
REPO_URL="GIT_REPO_URL"
BRANCH="GIT_BRANCH"
echo "Checking out code from $REPO_URL (branch: $BRANCH)..."
if [ -d ".git" ]; then
    git fetch origin
    git reset --hard origin/$BRANCH
    git clean -fd
else
    rm -rf * .[^.]*
    git clone -b $BRANCH "$REPO_URL" .
fi
export GIT_COMMIT=$(git rev-parse HEAD)
export GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Git Branch: $GIT_BRANCH | Commit: $GIT_COMMIT"

# Install dependencies
echo "Installing Robot Framework and dependencies..."
python3 -m pip install --quiet --upgrade pip --break-system-packages 2>/dev/null || python3 -m pip install --quiet --upgrade pip
python3 -m pip install --quiet --break-system-packages robotframework pymongo python-dotenv boto3 requests 2>/dev/null || python3 -m pip install --quiet robotframework pymongo python-dotenv boto3 requests

# MongoDB configuration
export MONGODB_URI='MONGODB_CONNECTION_STRING'
export MONGODB_COLLECTION="PROJECT_COLLECTION_NAME"
export JOB_NAME="$JOB_NAME"
export BUILD_NUMBER="$BUILD_NUMBER"
export BUILD_URL="$BUILD_URL"

# Create output directory
mkdir -p robot-results

# Run Robot Framework tests
echo "Executing Robot Framework tests..."
python3 -m robot \
    --outputdir robot-results \
    --xunit robot-results/xunit.xml \
    --variable PROJECT_ID:$PROJECT_ID \
    --variable PROJECT_SLUG:$PROJECT_SLUG \
    --name "PROJECT_NAME_Tests" \
    TEST_SUITE_PATH

# Capture Robot Framework exit code
ROBOT_EXIT_CODE=$?
echo "Robot Framework exit code: $ROBOT_EXIT_CODE"

# Parse Robot output.xml and upload to platform
echo "Parsing test results and uploading to platform..."
if [ -f "robot-results/output.xml" ]; then
    if [ -f "implementation/robot_framework_parser.py" ]; then
        python3 implementation/robot_framework_parser.py \
            --output-file robot-results/output.xml \
            --project-id $PROJECT_ID \
            --project-slug $PROJECT_SLUG \
            --build-number $BUILD_NUMBER \
            --job-name "$JOB_NAME"
    fi

    # Trigger AI analysis
    echo "Triggering AI analysis for failures..."
    curl -X POST http://host.docker.internal:5004/api/trigger-analysis \
        -H "Content-Type: application/json" \
        -d "{\"project_id\": $PROJECT_ID, \"project_slug\": \"$PROJECT_SLUG\"}" \
        2>/dev/null || echo "AI analysis trigger failed (non-critical)"
fi

echo "========================================="
echo "Tests completed!"
echo "Results uploaded to project_id: $PROJECT_ID"
echo "========================================="

# Exit with the robot exit code
exit $ROBOT_EXIT_CODE
```

**Replace These Placeholders:**

- `PROJECT_NAME` → Your project name
- `PROJECT_ID_NUMBER` → Next available ID (3, 4, 5...)
- `project_slug` → Lowercase project identifier
- `GIT_REPO_URL` → GitHub repository URL
- `GIT_BRANCH` → Branch name (main, develop, etc.)
- `MONGODB_CONNECTION_STRING` → Your MongoDB URI
- `PROJECT_COLLECTION_NAME` → MongoDB collection for this project
- `TEST_SUITE_PATH` → Path to test files

---

### Step 6: Build Triggers Configuration

#### Timer Trigger (Scheduled Builds)

```xml
<hudson.triggers.TimerTrigger>
  <spec>H */6 * * *</spec>
</hudson.triggers.TimerTrigger>
```

**Common Schedules:**

- Every 6 hours: `H */6 * * *`
- Daily at 2 AM: `0 2 * * *`
- Every weekday at 9 AM: `0 9 * * 1-5`
- Hourly: `H * * * *`
- Every 15 minutes: `H/15 * * * *`

#### SCM Polling (Check Git for Changes)

```xml
<hudson.triggers.SCMTrigger>
  <spec>H/15 * * * *</spec>
  <ignorePostCommitHooks>false</ignorePostCommitHooks>
</hudson.triggers.SCMTrigger>
```

---

### Step 7: Post-Build Actions

#### Archive Artifacts

```xml
<hudson.tasks.ArtifactArchiver>
  <artifacts>robot-results/**/*</artifacts>
  <allowEmptyArchive>true</allowEmptyArchive>
  <onlyIfSuccessful>false</onlyIfSuccessful>
  <fingerprint>false</fingerprint>
  <defaultExcludes>true</defaultExcludes>
  <caseSensitive>true</caseSensitive>
  <followSymlinks>false</followSymlinks>
</hudson.tasks.ArtifactArchiver>
```

#### Publish JUnit Results

```xml
<hudson.tasks.junit.JUnitResultArchiver>
  <testResults>robot-results/xunit.xml</testResults>
  <keepLongStdio>false</keepLongStdio>
  <healthScaleFactor>1.0</healthScaleFactor>
  <allowEmptyResults>true</allowEmptyResults>
</hudson.tasks.junit.JUnitResultArchiver>
```

---

### Step 8: Complete Configuration Assembly

**Using Python Script to Generate Config:**

Save as `generate-jenkins-job.py`:

```python
#!/usr/bin/env python3
import sys

def generate_choice_param(name, description, choices):
    """Generate choice parameter XML"""
    choices_xml = "\n              ".join(f"<string>{choice}</string>" for choice in choices)
    return f"""
        <hudson.model.ChoiceParameterDefinition>
          <name>{name}</name>
          <description>{description}</description>
          <choices class="java.util.Arrays$ArrayList">
            <a class="string-array">
              {choices_xml}
            </a>
          </choices>
        </hudson.model.ChoiceParameterDefinition>"""

def generate_boolean_param(name, description, default=True):
    """Generate boolean parameter XML"""
    return f"""
        <hudson.model.BooleanParameterDefinition>
          <name>{name}</name>
          <description>{description}</description>
          <defaultValue>{str(default).lower()}</defaultValue>
        </hudson.model.BooleanParameterDefinition>"""

def generate_job_config(project_config):
    """Generate complete Jenkins job configuration"""

    # Generate parameters
    parameters = []
    for param in project_config['parameters']:
        if param['type'] == 'choice':
            parameters.append(generate_choice_param(
                param['name'],
                param['description'],
                param['choices']
            ))
        elif param['type'] == 'boolean':
            parameters.append(generate_boolean_param(
                param['name'],
                param['description'],
                param.get('default', True)
            ))

    parameters_xml = "\n".join(parameters)

    # Generate shell script
    shell_script = project_config['shell_script']

    # Generate triggers
    triggers = f"""
    <hudson.triggers.TimerTrigger>
      <spec>{project_config['schedule']}</spec>
    </hudson.triggers.TimerTrigger>"""

    # Complete configuration
    config = f"""<?xml version='1.1' encoding='UTF-8'?>
<project>
  <actions/>
  <description>{project_config['description']}</description>
  <keepDependencies>false</keepDependencies>
  <properties>
    <jenkins.model.BuildDiscarderProperty>
      <strategy class="hudson.tasks.LogRotator">
        <daysToKeep>30</daysToKeep>
        <numToKeep>50</numToKeep>
        <artifactDaysToKeep>-1</artifactDaysToKeep>
        <artifactNumToKeep>-1</artifactNumToKeep>
        <removeLastBuild>false</removeLastBuild>
      </strategy>
    </jenkins.model.BuildDiscarderProperty>
    <hudson.model.ParametersDefinitionProperty>
      <parameterDefinitions>{parameters_xml}
      </parameterDefinitions>
    </hudson.model.ParametersDefinitionProperty>
  </properties>
  <scm class="hudson.scm.NullSCM"/>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers>{triggers}
  </triggers>
  <concurrentBuild>false</concurrentBuild>
  <builders>
    <hudson.tasks.Shell>
      <command>{shell_script}</command>
      <configuredLocalRules/>
    </hudson.tasks.Shell>
  </builders>
  <publishers>
    <hudson.tasks.ArtifactArchiver>
      <artifacts>robot-results/**/*</artifacts>
      <allowEmptyArchive>true</allowEmptyArchive>
      <onlyIfSuccessful>false</onlyIfSuccessful>
      <fingerprint>false</fingerprint>
      <defaultExcludes>true</defaultExcludes>
      <caseSensitive>true</caseSensitive>
      <followSymlinks>false</followSymlinks>
    </hudson.tasks.ArtifactArchiver>
    <hudson.tasks.junit.JUnitResultArchiver>
      <testResults>robot-results/xunit.xml</testResults>
      <keepLongStdio>false</keepLongStdio>
      <healthScaleFactor>1.0</healthScaleFactor>
      <allowEmptyResults>true</allowEmptyResults>
    </hudson.tasks.junit.JUnitResultArchiver>
  </publishers>
  <buildWrappers/>
</project>"""

    return config

# Example usage
if __name__ == "__main__":
    # Define your project configuration
    project_config = {
        'description': 'MyNewProject Test Automation - Robot Framework tests',
        'schedule': 'H */6 * * *',
        'parameters': [
            {
                'name': 'TEST_TYPE',
                'type': 'choice',
                'description': 'Select test type',
                'choices': ['Smoke', 'Regression', 'Sanity', 'All']
            },
            {
                'name': 'SEND_NOTIFICATIONS',
                'type': 'boolean',
                'description': 'Send notifications on completion',
                'default': True
            }
        ],
        'shell_script': """#!/bin/bash
echo "MyNewProject Tests"
export PROJECT_ID="3"
export PROJECT_SLUG="mynewproject"
# ... rest of shell script ...
"""
    }

    # Generate configuration
    config_xml = generate_job_config(project_config)

    # Save to file
    with open('mynewproject-job-config.xml', 'w') as f:
        f.write(config_xml)

    print("✅ Configuration generated: mynewproject-job-config.xml")
```

**Run the script:**

```bash
python3 generate-jenkins-job.py
```

---

### Step 9: Apply Configuration to Jenkins

#### Method A: Copy to Jenkins Container

```bash
# Copy XML to Jenkins jobs directory
cat mynewproject-job-config.xml | docker exec -i ddn-jenkins bash -c "cat > /var/jenkins_home/jobs/MyNewProject-Tests/config.xml"

# Verify file size (should not be 0)
docker exec ddn-jenkins bash -c "ls -lh /var/jenkins_home/jobs/MyNewProject-Tests/config.xml"

# Reload Jenkins configuration
curl -X POST http://localhost:8081/reload
# OR restart Jenkins
docker restart ddn-jenkins
```

#### Method B: Manual Creation via UI (Recommended)

1. Open Jenkins: http://localhost:8081/
2. Click "New Item"
3. Enter job name
4. Select "Freestyle project"
5. Configure using UI (paste shell script, add parameters, etc.)
6. Save

---

## 🎯 Complete Example: Creating "QA-Automation" Project

### 1. Define Project

```ini
PROJECT_NAME=QA-Automation
PROJECT_ID=4
PROJECT_SLUG=qa-automation
REPO_URL=https://github.com/myorg/qa-automation-tests
BRANCH=main
COLLECTION=qa_automation_test_failures
JIRA_PROJECT=QA
PINECONE_NAMESPACE=qa-automation
```

### 2. Create Shell Script

Save as `qa-automation-build-script.sh`:

```bash
#!/bin/bash
echo "========================================="
echo "QA Automation Tests (Robot Framework)"
echo "Build: $BUILD_NUMBER"
echo "========================================="

export PROJECT_ID="4"
export PROJECT_SLUG="qa-automation"

REPO_URL="https://github.com/myorg/qa-automation-tests"
BRANCH="main"

if [ -d ".git" ]; then
    git fetch origin && git reset --hard origin/$BRANCH
else
    git clone -b $BRANCH "$REPO_URL" .
fi

python3 -m pip install --quiet --break-system-packages robotframework pymongo python-dotenv boto3 requests

export MONGODB_URI='mongodb+srv://...'
export MONGODB_COLLECTION="qa_automation_test_failures"

mkdir -p robot-results

python3 -m robot \
    --outputdir robot-results \
    --xunit robot-results/xunit.xml \
    --variable PROJECT_ID:$PROJECT_ID \
    --variable PROJECT_SLUG:$PROJECT_SLUG \
    tests/

ROBOT_EXIT_CODE=$?

if [ -f "robot-results/output.xml" ]; then
    python3 implementation/robot_framework_parser.py \
        --output-file robot-results/output.xml \
        --project-id $PROJECT_ID \
        --project-slug $PROJECT_SLUG \
        --build-number $BUILD_NUMBER \
        --job-name "$JOB_NAME"

    curl -X POST http://host.docker.internal:5004/api/trigger-analysis \
        -H "Content-Type: application/json" \
        -d "{\"project_id\": $PROJECT_ID, \"project_slug\": \"$PROJECT_SLUG\"}"
fi

exit $ROBOT_EXIT_CODE
```

### 3. Generate Configuration

Use the Python script or manually create XML with the shell script above.

### 4. Apply to Jenkins

```bash
# Create job directory
docker exec ddn-jenkins bash -c "mkdir -p /var/jenkins_home/jobs/QA-Automation-Tests"

# Copy configuration
cat qa-automation-job-config.xml | docker exec -i ddn-jenkins bash -c "cat > /var/jenkins_home/jobs/QA-Automation-Tests/config.xml"

# Restart Jenkins
docker restart ddn-jenkins
```

### 5. Verify and Test

```bash
# Wait for Jenkins to start
sleep 60

# Check job is visible
curl http://localhost:8081/ | grep "QA-Automation-Tests"

# Trigger first build
curl -X POST "http://localhost:8081/job/QA-Automation-Tests/build?delay=0sec"
```

---

## 📋 Checklist for New Project Jobs

Before creating a new Jenkins job:

### Prerequisites:
- [ ] Assign unique PROJECT_ID (next available number)
- [ ] Define PROJECT_SLUG (lowercase, no spaces)
- [ ] Create GitHub repository with tests
- [ ] Set up MongoDB collection (project_slug_test_failures)
- [ ] Configure Jira project key
- [ ] Create Pinecone namespace
- [ ] Update PostgreSQL projects table

### Configuration:
- [ ] Define job parameters (TEST_TYPE, PLATFORM, etc.)
- [ ] Create shell script with correct PROJECT_ID
- [ ] Set up build triggers (schedule)
- [ ] Configure post-build actions (artifacts, JUnit)
- [ ] Test Git repository access

### Testing:
- [ ] Verify job appears in Jenkins
- [ ] Run first test build
- [ ] Check MongoDB has data with correct project_id
- [ ] Verify PostgreSQL entries with correct project_id
- [ ] Confirm Dashboard shows project-specific data
- [ ] Test Jira ticket creation
- [ ] Verify data isolation from other projects

---

## 🔄 Automation Script for Future Jobs

Save as `create-new-jenkins-job.sh`:

```bash
#!/bin/bash

# Usage: ./create-new-jenkins-job.sh <project-name> <project-id> <repo-url> <branch>

PROJECT_NAME=$1
PROJECT_ID=$2
REPO_URL=$3
BRANCH=$4
PROJECT_SLUG=$(echo "$PROJECT_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')

echo "Creating Jenkins job for: $PROJECT_NAME"
echo "Project ID: $PROJECT_ID"
echo "Project Slug: $PROJECT_SLUG"
echo "Repository: $REPO_URL"
echo "Branch: $BRANCH"

# Generate shell script
cat > "${PROJECT_SLUG}-build.sh" << 'EOF'
#!/bin/bash
export PROJECT_ID="PROJECT_ID_PLACEHOLDER"
export PROJECT_SLUG="PROJECT_SLUG_PLACEHOLDER"
# ... rest of script template ...
EOF

# Replace placeholders
sed -i "s/PROJECT_ID_PLACEHOLDER/$PROJECT_ID/g" "${PROJECT_SLUG}-build.sh"
sed -i "s/PROJECT_SLUG_PLACEHOLDER/$PROJECT_SLUG/g" "${PROJECT_SLUG}-build.sh"

echo "✅ Build script created: ${PROJECT_SLUG}-build.sh"
echo "Next: Use this script in Jenkins job configuration"
```

---

## 📚 Key Takeaways

### What Worked for Guruttava:

1. ✅ **Shell script approach** (not Pipeline from SCM)
2. ✅ **Hardcoded PROJECT_ID and PROJECT_SLUG** in script
3. ✅ **Direct Git clone** in build script
4. ✅ **MongoDB collection naming** pattern: `{project_slug}_test_failures`
5. ✅ **Automatic AI analysis** trigger via curl
6. ✅ **XUnit output** for Jenkins integration

### Critical Points:

- **PROJECT_ID must be unique** for each project
- **PROJECT_SLUG must match** MongoDB collection prefix
- **Git branch must exist** before configuring job
- **MongoDB URI** can be shared, but collections are separate
- **Manual trigger API URL** must be accessible from Jenkins container
- **Parser script** must exist in repository (`robot_framework_parser.py`)

---

**Use this guide to create unlimited Jenkins jobs for your multi-tenant platform!** 🚀
