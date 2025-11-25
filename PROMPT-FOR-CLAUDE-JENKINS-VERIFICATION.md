# Prompt for Claude - Jenkins Robot Framework Verification

## What to Tell Claude:

```
Hi Claude! I've added Robot Framework to Jenkins. Here's what I did:

1. ✅ Opened Jenkins job: DDN-Nightly-Tests configuration
2. ✅ Added a new "Execute Windows batch command" build step
3. ✅ Pasted the complete Robot Framework command with:
   - Python dependency installation (robotframework, pymongo, boto3, requests)
   - MongoDB URI configuration
   - Robot test execution with mongodb_robot_listener.py

Please verify:
- Is the Jenkins configuration correct?
- Do I need to run the build now?
- How do I check if the mongodb_robot_listener.py captured failures in MongoDB?
- What should I see in the Dashboard after the build completes?

[Attach screenshot of Jenkins configuration page showing the 3 build steps]
```

## What Claude Will Check:

1. **Build step order** - Mocha tests first, then Robot Framework
2. **Dependencies** - All required Python packages are installed
3. **MongoDB URI** - Connection string is correct
4. **Listener path** - `implementation\mongodb_robot_listener.py` path is valid
5. **Test path** - `robot-tests\` directory exists and has test files

## Next Steps After Claude Verifies:

1. Click "Save" in Jenkins
2. Click "Build Now"
3. Wait for build to complete (will take 2-3 minutes)
4. Run verification command:
   ```powershell
   Invoke-WebRequest -Uri "http://localhost:5006/api/failures?limit=5" | ConvertFrom-Json | ConvertTo-Json -Depth 5
   ```
5. Check if new failures appear with:
   - ✅ `suite_name` populated (e.g., "DDN Basic Tests")
   - ✅ `pass_count`, `fail_count`, `total_count` populated
   - ✅ `build_id` format: "Robot-Framework-Jenkins-Build-23" (or similar)

## Success Criteria:

- ✅ MongoDB has NEW failures (count > 833)
- ✅ Failures have complete suite metadata
- ✅ Dashboard shows Robot Framework test results
- ✅ Bug #1 and Bug #3 are CONFIRMED FIXED!
