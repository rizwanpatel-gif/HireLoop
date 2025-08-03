# Google Calendar Integration Setup Guide

This guide walks you through setting up Google Calendar integration for the Interview Scheduling System.

## Prerequisites

1. **Google Cloud Console Account**: You need access to Google Cloud Console
2. **Google Calendar API**: Enable the Google Calendar API for your project
3. **OAuth2 Credentials**: Create OAuth2 credentials for your application

## Step 1: Google Cloud Console Setup

### 1.1 Create a New Project (or use existing)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name: `interview-scheduling-system`
4. Click "Create"

### 1.2 Enable Google Calendar API
1. In the Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Google Calendar API"
3. Click on "Google Calendar API"
4. Click "Enable"

### 1.3 Create OAuth2 Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" (for testing) or "Internal" (for organization use)
   - Fill in app name: "Interview Scheduling System"
   - Add your email as a test user
4. For application type, choose "Desktop application"
5. Enter name: "Interview Scheduling Desktop"
6. Click "Create"
7. Download the JSON file and save it as `credentials.json` in your project root

## Step 2: Environment Configuration

### 2.1 Update `.env` file
Add these variables to your `.env` file:

```bash
# Google Calendar Configuration
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_TOKEN_FILE=token.json
GOOGLE_TIMEZONE=Asia/Kolkata
GOOGLE_CALENDAR_ID=primary

# Optional: For service account (advanced usage)
GOOGLE_SERVICE_ACCOUNT_FILE=service_account.json
GOOGLE_ADMIN_EMAIL=admin@yourcompany.com
```

### 2.2 Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 3: Authentication Setup

### 3.1 First-time Authentication
Run the authentication script to set up OAuth2 tokens:

```python
# test_calendar_auth.py
from google_calendar_service import GoogleCalendarService

def test_authentication():
    service = GoogleCalendarService()
    if service.authenticate():
        print("✅ Authentication successful!")
        
        # Test basic functionality
        availability = service.get_availability(
            email="your-email@gmail.com",
            start_date=datetime.now(),
            end_date=datetime.now() + timedelta(days=7)
        )
        print(f"Found {len(availability['free'])} free slots")
    else:
        print("❌ Authentication failed!")

if __name__ == "__main__":
    test_authentication()
```

Run: `python test_calendar_auth.py`

This will:
1. Open a browser window for OAuth2 authorization
2. Ask you to sign in to Google and grant permissions
3. Save the token to `token.json` for future use

## Step 4: API Integration

### 4.1 Test Calendar Endpoints
Start your FastAPI server:
```bash
python api.py
```

### 4.2 Test Available Endpoints

#### Check Calendar Service Health
```bash
curl http://localhost:8000/api/calendar/health
```

#### Check User Availability
```bash
curl -X POST "http://localhost:8000/api/calendar/availability/check" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "interviewer@company.com",
    "start_date": "2025-08-02T09:00:00",
    "end_date": "2025-08-02T18:00:00",
    "duration_minutes": 60
  }'
```

#### Find Mutual Availability
```bash
curl -X POST "http://localhost:8000/api/calendar/availability/mutual" \
  -H "Content-Type: application/json" \
  -d '{
    "emails": ["interviewer1@company.com", "interviewer2@company.com"],
    "start_date": "2025-08-02T09:00:00",
    "end_date": "2025-08-02T18:00:00",
    "duration_minutes": 60,
    "max_suggestions": 5
  }'
```

#### Create Calendar Event for Interview
```bash
curl -X POST "http://localhost:8000/api/calendar/events/create" \
  -H "Content-Type: application/json" \
  -d '{
    "interview_id": 1,
    "send_invitations": true,
    "additional_attendees": ["hr@company.com"]
  }'
```

## Step 5: React Frontend Integration

### 5.1 Calendar API Service
Add to your `src/api/services.js`:

```javascript
// Calendar API
export const calendarAPI = {
  checkHealth: () => apiClient.get('/api/calendar/health'),
  
  checkAvailability: (availabilityData) => 
    apiClient.post('/api/calendar/availability/check', availabilityData),
  
  findMutualAvailability: (mutualData) => 
    apiClient.post('/api/calendar/availability/mutual', mutualData),
  
  createEvent: (eventData) => 
    apiClient.post('/api/calendar/events/create', eventData),
  
  updateEvent: (interviewId, updateData) => 
    apiClient.put(`/api/calendar/events/${interviewId}`, updateData),
  
  cancelEvent: (interviewId, sendUpdates = 'all') => 
    apiClient.delete(`/api/calendar/events/${interviewId}?send_updates=${sendUpdates}`),
  
  suggestTimes: (params) => 
    apiClient.get('/api/calendar/suggest-times', { params }),
  
  scheduleWithCalendar: (interviewId, checkAvailability = true) => 
    apiClient.post(`/api/calendar/interviews/schedule-with-calendar?interview_id=${interviewId}&check_availability=${checkAvailability}`)
};
```

### 5.2 React Component Example
```javascript
// AvailabilityChecker.js
import React, { useState } from 'react';
import { calendarAPI } from '../api/services';

const AvailabilityChecker = () => {
  const [email, setEmail] = useState('');
  const [availability, setAvailability] = useState(null);
  const [loading, setLoading] = useState(false);

  const checkAvailability = async () => {
    setLoading(true);
    try {
      const response = await calendarAPI.checkAvailability({
        email,
        start_date: new Date().toISOString(),
        end_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
        duration_minutes: 60
      });
      setAvailability(response.data);
    } catch (error) {
      console.error('Error checking availability:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="availability-checker">
      <h3>Check Availability</h3>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Enter email address"
      />
      <button onClick={checkAvailability} disabled={loading}>
        {loading ? 'Checking...' : 'Check Availability'}
      </button>
      
      {availability && (
        <div className="availability-results">
          <h4>Free Slots:</h4>
          {availability.free_slots.map((slot, index) => (
            <div key={index} className="time-slot">
              {new Date(slot.start).toLocaleString()} - {new Date(slot.end).toLocaleString()}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AvailabilityChecker;
```

## Step 6: Troubleshooting

### Common Issues and Solutions

#### 1. "Credentials file not found"
- Ensure `credentials.json` is in the project root
- Check the `GOOGLE_CREDENTIALS_FILE` environment variable

#### 2. "Permission denied" errors
- Verify OAuth2 scopes in the Google Cloud Console
- Re-run authentication: `rm token.json && python test_calendar_auth.py`

#### 3. "Calendar not found" errors
- Check if the email address has a Google Calendar
- Verify the user has granted calendar permissions

#### 4. "Rate limit exceeded" errors
- Implement exponential backoff in your requests
- Consider caching availability data

#### 5. Timezone issues
- Ensure all datetime objects are timezone-aware
- Verify the `GOOGLE_TIMEZONE` environment variable

### Debug Mode
Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### OAuth2 Consent Screen
For production deployment:
1. Complete OAuth consent screen verification in Google Cloud Console
2. Add your domain to authorized domains
3. Submit for verification if using sensitive scopes

## Step 7: Production Considerations

### 7.1 Service Account (Optional)
For server-to-server authentication:
1. Create a service account in Google Cloud Console
2. Download the service account key file
3. Enable domain-wide delegation
4. Update configuration to use service account

### 7.2 Security Best Practices
- Store credentials securely (use environment variables)
- Implement proper error handling
- Use HTTPS in production
- Regularly rotate credentials
- Monitor API usage and quotas

### 7.3 Scaling Considerations
- Implement connection pooling
- Cache availability data when appropriate
- Use background tasks for calendar operations
- Monitor API quotas and implement rate limiting

## API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/calendar/health` | GET | Check calendar service health |
| `/api/calendar/availability/check` | POST | Check user availability |
| `/api/calendar/availability/mutual` | POST | Find mutual availability |
| `/api/calendar/events/create` | POST | Create calendar event |
| `/api/calendar/events/{id}` | PUT | Update calendar event |
| `/api/calendar/events/{id}` | DELETE | Cancel calendar event |
| `/api/calendar/suggest-times` | GET | Get suggested interview times |
| `/api/calendar/interviews/schedule-with-calendar` | POST | Schedule interview with calendar |

This completes the Google Calendar integration setup for your Interview Scheduling System!
