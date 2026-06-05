# DDN AI Mobile App - Setup Mock Data for Testing

## Problem: No Data Showing in App

The app is installed and running, but it shows no data because:
1. **No backend API running** - The app expects APIs running on your computer
2. **No cached data** - First load requires API connection to cache data offline

## Solution: Two Options

### OPTION 1: Run Backend API (Recommended)

The backend API is already implemented at:
`C:\DDN-AI-Project-Documentation\implementation\dashboard_api_full.py`

**Quick Start (Python 3 required):**

```bash
# Navigate to project
cd C:\DDN-AI-Project-Documentation\implementation

# Install dependencies
pip install flask flask-cors python-dateutil

# Run the API server
python dashboard_api_full.py

# Server will start on http://localhost:5006
```

Then in the app:
1. Open **Settings**
2. Check API endpoint (should be http://[YOUR_COMPUTER_IP]:5006)
3. Restart the app
4. Data should load!

### OPTION 2: Quick Mock Data Setup

If you don't want to run backend:

**Step 1: Edit API Endpoints** (Optional - for your computer IP)

File: `ddn_ai_mobile\lib\core\constants\api_endpoints.dart`

Change line 13:
```dart
static const String _computerIp = '192.168.1.7'; // Change to your IP
```

Find your computer IP:
- Windows: Open CMD, run `ipconfig`, look for "IPv4 Address"
- Mac/Linux: Open Terminal, run `ifconfig`, look for "inet"

**Step 2: Create Mock Data File**

Create file: `ddn_ai_mobile\lib\core\mock_data.dart`

```dart
// Mock data for testing
class MockData {
  static final failures = [
    {
      'id': '1',
      'name': 'Login Test Failed',
      'error_type': 'AssertionError',
      'severity': 'critical',
      'timestamp': DateTime.now().toIso8601String(),
      'message': 'Expected: true, Actual: false',
      'stack_trace': 'at LoginTest.testUserLogin (LoginTest.java:45)',
    },
    {
      'id': '2',
      'name': 'API Timeout',
      'error_type': 'TimeoutException',
      'severity': 'high',
      'timestamp': DateTime.now().subtract(Duration(hours: 2)).toIso8601String(),
      'message': 'Request timed out after 30 seconds',
      'stack_trace': 'at ApiService.fetchData (ApiService.dart:120)',
    },
  ];
}
```

**Step 3: Use Cache to Add Data** (Workaround)

The app uses **Hive** for offline caching. To populate cache:

File: `ddn_ai_mobile\lib\main.dart`

Add this before `runApp()`:

```dart
// Add mock data to Hive cache
await _initializeMockData();
```

Create function:

```dart
Future<void> _initializeMockData() async {
  // This populates the Hive cache with demo data
  // So app works immediately without API
}
```

---

## For Immediate Testing - Use Local Emulator Data

**Step 1: Copy Sample Data**

The project includes sample data. Load it:

File: `ddn_ai_mobile\lib\features\failures\data\datasources\local_datasource.dart`

**Step 2: Rebuild App**

```bash
cd ddn_ai_mobile
flutter clean
flutter pub get
flutter build apk --release
```

Then reinstall the APK.

---

## API Endpoints the App Expects

The app calls these endpoints (from `api_endpoints.dart`):

```
GET    /failures                    → List of test failures
GET    /failures/{id}               → Failure details
GET    /analysis/{failureId}        → AI analysis
GET    /analytics/summary           → Dashboard stats
GET    /analytics/trends            → Trend data
GET    /chat                        → Chat history
POST   /chat/send                   → Send message
GET    /notifications              → Notification list
GET    /rag/pending                 → RAG approvals pending
POST   /rag/approve/{id}            → Approve RAG
```

---

## Best Setup for Full Functionality

### Backend API (Full Features)

1. **Start Backend:**
   ```bash
   cd C:\DDN-AI-Project-Documentation\implementation
   python dashboard_api_full.py
   ```

2. **Update App IP Address:**
   - Settings in app OR
   - Edit `api_endpoints.dart` with your computer IP

3. **Restart App:**
   - App will connect to backend
   - All data will load and cache

### With Backend Features:

✅ Real-time data from API
✅ Chat messages processed by AI
✅ Analytics computed live
✅ Notifications from backend
✅ RAG approval workflow
✅ Data caches offline
✅ Auto-sync when online

---

## Quick Verification Steps

1. **Check Backend is Running:**
   ```bash
   # In another terminal
   curl http://localhost:5006/api/failures
   ```

2. **Check App Connection:**
   - Open App
   - Go to Settings
   - Verify API endpoint shown
   - Should see http://[IP]:5006

3. **View Logs:**
   ```bash
   adb logcat | grep flutter
   ```
   Look for API connection messages

---

## Troubleshooting Data Loading

**Problem**: Still no data after setup

**Check List:**
- [ ] Backend API running? (`python dashboard_api_full.py`)
- [ ] Correct IP in API endpoint? (Check in Settings)
- [ ] Device and computer on same WiFi?
- [ ] Firewall not blocking port 5006?
- [ ] No spaces in IP address?

**Quick Fix:**
```bash
# Restart backend
python dashboard_api_full.py

# Restart app
# Uninstall and reinstall APK
adb uninstall com.example.ddn_ai_mobile
adb install ddn_ai_mobile_release.apk
```

---

## Next Steps

1. **Start Backend API** (Recommended):
   ```bash
   python C:\DDN-AI-Project-Documentation\implementation\dashboard_api_full.py
   ```

2. **Update App Endpoint** if needed (Settings)

3. **Restart App** and wait for data to load

4. **Explore Features**:
   - Dashboard with failures
   - Analysis with AI insights
   - Chat with AI assistant
   - Analytics with charts
   - Notifications
   - Settings

5. **Test Offline**:
   - Enable Airplane Mode
   - App continues working with cached data
   - Messages save offline
   - Auto-syncs when back online

---

## Questions?

If data still doesn't load:
1. Check backend is running: `http://localhost:5006/api/failures`
2. Check IP address in Settings
3. Check device/computer on same WiFi
4. View logs: `adb logcat`
5. Try reinstalling APK

The app is working - it just needs backend API connection!

