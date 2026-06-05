# Jenkins Access Guide

## Current Status
✅ Jenkins is **RUNNING** at http://localhost:8081/
✅ Login page is accessible
⚠️  Admin password needed

---

## Option 1: Reset Jenkins Admin Password (RECOMMENDED)

### Step 1: Stop Jenkins
```bash
docker compose stop jenkins
```

### Step 2: Disable Security Temporarily
```bash
# Add this line to config.xml to disable security temporarily
docker exec ddn-jenkins bash -c "sed -i 's/<useSecurity>true<\/useSecurity>/<useSecurity>false<\/useSecurity>/g' /var/jenkins_home/config.xml"
```

### Step 3: Restart Jenkins
```bash
docker compose start jenkins
# Wait 30 seconds for Jenkins to start
```

### Step 4: Access Jenkins Without Login
Open browser: http://localhost:8081/

### Step 5: Reset Admin Password
1. Click "Manage Jenkins" → "Security" → "Manage Users"
2. Click on "admin" user
3. Click "Configure"
4. Enter new password in "Password" and "Confirm password" fields
5. Click "Save"

### Step 6: Re-enable Security
```bash
docker exec ddn-jenkins bash -c "sed -i 's/<useSecurity>false<\/useSecurity>/<useSecurity>true<\/useSecurity>/g' /var/jenkins_home/config.xml"
```

### Step 7: Restart Jenkins
```bash
docker compose restart jenkins
```

Now login with:
- **Username**: `admin`
- **Password**: (the one you just set)

---

## Option 2: Create New Admin User via Script

Run this script to create a new admin user:

```bash
docker exec ddn-jenkins bash -c "cat > /tmp/create-admin.groovy << 'EOF'
import jenkins.model.*
import hudson.security.*

def instance = Jenkins.getInstance()
def hudsonRealm = new HudsonPrivateSecurityRealm(false)
hudsonRealm.createAccount(\"admin2\", \"admin2password\")
instance.setSecurityRealm(hudsonRealm)
instance.save()

println \"New admin user created:\"
println \"Username: admin2\"
println \"Password: admin2password\"
EOF
"

# Execute the script
docker exec ddn-jenkins bash -c "java -jar /usr/share/jenkins/jenkins.war groovy /tmp/create-admin.groovy"
```

Then login with:
- **Username**: `admin2`
- **Password**: `admin2password`

---

## Option 3: Check if Browser is Blocking

### Try These:
1. **Clear browser cache** (Ctrl+Shift+Delete)
2. **Try incognito/private mode**
3. **Try different browser** (Chrome, Firefox, Edge)
4. **Check if localhost resolves**:
   ```bash
   ping localhost
   # Should respond from 127.0.0.1
   ```

5. **Try 127.0.0.1 instead**:
   - http://127.0.0.1:8081/

---

## Option 4: Completely Reset Jenkins (NUCLEAR OPTION)

⚠️  **WARNING**: This will delete all Jenkins jobs and configuration!

```bash
# Stop Jenkins
docker compose stop jenkins

# Delete Jenkins data
rm -rf D:/rancher-storage/volumes/jenkins-data/*

# Start Jenkins (fresh install)
docker compose start jenkins

# Wait 2 minutes for first-time setup
# Check initial password:
docker exec ddn-jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Then:
1. Open http://localhost:8081/
2. Enter the initial admin password
3. Click "Install suggested plugins"
4. Create admin user
5. Start using Jenkins!

---

## Quick Test - See if You Can Access

Open your browser (Chrome, Firefox, or Edge) and navigate to:
```
http://localhost:8081/login
```

You should see:
- **Title**: "Sign in to Jenkins"
- **Username field**
- **Password field**
- **Sign in button**

If you see this page, Jenkins is working! You just need credentials.

---

## Recommended Credentials for New Setup

If you reset Jenkins, use these credentials:
- **Username**: `admin`
- **Password**: `Jenkins@2024!` (or whatever you prefer)

---

## After Logging In - Import Jobs

Once you're logged in, follow these steps to import the DDN and Guruttava jobs:

### Import DDN Job
1. Click "New Item"
2. Enter name: `DDN-Tests`
3. Select "Pipeline"
4. Click "OK"
5. Under "Pipeline" section:
   - Definition: "Pipeline script from SCM"
   - SCM: Git
   - Repository URL: `https://github.com/Sushrut-01/ddn-jenkins-testing.git`
   - Branch: `*/main`
   - Script Path: `Jenkinsfile`
6. Click "Save"

### Import Guruttava Job
1. Click "New Item"
2. Enter name: `Guruttava-Tests`
3. Select "Pipeline"
4. Click "OK"
5. Under "Pipeline" section:
   - Definition: "Pipeline script from SCM"
   - SCM: Git
   - Repository URL: `https://github.com/Sushrut-01/gurutattva-e2e-automation`
   - Branch: `*/main`
   - Script Path: `Jenkinsfile`
6. Click "Save"

---

## What You'll See After Import

### DDN-Tests Job
- **Parameters**: TEST_TYPE, TEST_SUITE, SEND_NOTIFICATIONS, RUN_PERFORMANCE_TESTS
- **Stages**: Checkout → Setup → Run Tests (Basic/Advanced/API/UI) → Parse Results → Upload to Platform
- **PROJECT_ID**: 1 (hardcoded in pipeline)

### Guruttava-Tests Job
- **Parameters**: PLATFORM, TEST_TYPE, DEVICE_NAME, APP_PATH
- **Stages**: Checkout → Setup → Verify Appium → Run Tests (Android/iOS/Web) → Parse Results → Upload to Platform
- **PROJECT_ID**: 2 (hardcoded in pipeline)

---

## Need Help?

**Jenkins not starting?**
```bash
docker compose logs jenkins --tail 50
```

**Can't access localhost:8081?**
```bash
# Check if port is in use
netstat -ano | findstr :8081

# Check Jenkins is running
docker ps | grep jenkins
```

**Forgot password?**
- Use Option 1 to reset it

---

**Choose Option 1 (Reset Password) if you want to keep existing jobs**
**Choose Option 4 (Complete Reset) if you want a fresh start**
