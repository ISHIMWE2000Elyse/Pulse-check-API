# Pulse-Check API ("Watchdog" Sentinel)

A backend monitoring service implementing a **Dead Man’s Switch** for remote devices.  
Devices must periodically send heartbeats to remain marked as **active**.  
If a heartbeat is missed before timeout expires, the system automatically triggers an alert.

---

## Overview

CritMon Servers Inc. monitors remote infrastructure such as solar farms and weather stations located in areas with unreliable connectivity.

This service solves the problem of undetected outages by:

- Registering devices with countdown timers
- Resetting timers on heartbeat signals
- Triggering alerts when devices stop reporting
- Allowing monitoring to be paused during maintenance

---

## Architecture Diagram

```text
Device → API
   ↓
Register Monitor
   ↓
Start Timer
   ↓
Heartbeat Received?
 ├── Yes → Reset Timer
 ├── No → Timer Expires → Trigger Alert
```

---

## Tech Stack

- Python
- FastAPI
- Uvicorn
- Asyncio
- In-memory Dictionary Store

---

## Setup Instructions

### 1. Clone Repository

```bash
git clone <your-repository-link>
cd pulse-check-api
```

### 2. Install Dependencies

```bash
pip install fastapi uvicorn
```

### 3. Run Application

```bash
uvicorn main:app --reload
```

### 4. Open API Docs

```text
http://127.0.0.1:8000/docs
```

---

## API Documentation

---

### Register a Monitor

**POST** `/monitors`

#### Request Body

```json
{
  "id": "device-123",
  "timeout": 60,
  "alert_email": "admin@critmon.com"
}
```

#### Response

```json
{
  "message": "Monitor created for device-123"
}
```

#### Status Code

`201 Created`

---

### Send Heartbeat

**POST** `/monitors/{id}/heartbeat`

#### Response

```json
{
  "message": "Heartbeat received for device-123"
}
```

#### Status Code

`200 OK`

---

### Pause Monitoring

**POST** `/monitors/{id}/pause`

#### Response

```json
{
  "message": "Monitor device-123 paused"
}
```

#### Status Code

`200 OK`

---

### Get Monitor Status

**GET** `/monitors/{id}`

#### Response

```json
{
  "id": "device-123",
  "status": "active",
  "timeout": 60
}
```

---

## Alert Behavior

If a device fails to send heartbeat before timeout:

```json
{
  "ALERT": "Device device-123 is down!",
  "time": "2026-04-25T12:00:00"
}
```

The monitor status changes to:

```text
down
```

---

## System States

Each monitor can be in one of three states:

- `active` → Device is healthy
- `paused` → Monitoring temporarily disabled
- `down` → Timeout expired / Alert triggered

---

## Design Decisions

### Async Timer Management

Used `asyncio.create_task()` for non-blocking per-device timers.

**Why?**

- Efficient concurrency
- No thread blocking
- Scales better for many monitors

---

### In-Memory Store

Used Python dictionary:

```text
device_id → { timeout, status, task }
```

**Why?**

- Fast lookup
- Simple implementation for prototype/demo

---

### Automatic Timer Reset

Heartbeat cancels previous timer and starts a new one.

**Why?**

Ensures timeout always counts from latest heartbeat.

---

## Developer’s Choice Feature

### Added: Monitor Status Endpoint

**Endpoint:** `GET /monitors/{id}`

**Purpose:**

Allows operators/dashboard systems to query the current status of any monitor.

**Why Added?**

Real-world monitoring systems need visibility into current device state for dashboards, audits, and troubleshooting.

Implemented pause/resume functionality to allow maintenance without triggering alerts.

---

## Example Test Flow

### Register Device

```bash
curl -X POST http://127.0.0.1:8000/monitors \
-H "Content-Type: application/json" \
-d '{"id":"device-123","timeout":10,"alert_email":"admin@critmon.com"}'
```

---

### Send Heartbeat

```bash
curl -X POST http://127.0.0.1:8000/monitors/device-123/heartbeat
```

---

### Pause Monitor

```bash
curl -X POST http://127.0.0.1:8000/monitors/device-123/pause
```

---

## Project Structure

```text
.
├── main.py
├── README.md
└── requirements.txt
```

---

## Error Handling

| Scenario | Status Code |
|---------|------------|
| Monitor Not Found | 404 |
| Duplicate Monitor Registration | 400 |
| Invalid Input | 422 |

---

## Future Improvements

- Redis/PostgreSQL Persistence
- Real Email/SMS Alerts
- Distributed Timer Management
- Monitoring Dashboard UI

---

## Conclusion

This project demonstrates:

- Stateful timer management
- Async concurrency handling
- Failure detection patterns
- RESTful API design
- Production-minded backend engineering

---

## Project Checklist

- [x] Public Repository
- [x] Clean Codebase
- [x] Architecture Diagram Included
- [x] API Documentation Included
- [x] Multiple Meaningful Commits
- [x] Server Runs Successfully

---