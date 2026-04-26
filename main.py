from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import threading
import time

app = FastAPI()

# In-memory store
monitors = {}
lock = threading.Lock()


# DATA MODELS
class MonitorCreate(BaseModel):
    id: str
    timeout: int
    alert_email: EmailStr


# ALERT FUNCTION
def trigger_alert(device_id):
    with lock:
        monitor = monitors.get(device_id)
        if not monitor:
            return

        if monitor["status"] == "paused":
            return

        monitor["status"] = "down"

    print({
        "ALERT": f"Device {device_id} is down!",
        "time": time.time()
    })


# TIMER MANAGEMENT
def start_timer(device_id, timeout):
    timer = threading.Timer(timeout, trigger_alert, args=[device_id])
    timer.start()
    return timer


# ENDPOINT 1: CREATE MONITOR
@app.post("/monitors", status_code=201)
def create_monitor(data: MonitorCreate):

    with lock:
        if data.id in monitors:
            raise HTTPException(status_code=409, detail="Monitor already exists")

        timer = start_timer(data.id, data.timeout)

        monitors[data.id] = {
            "id": data.id,
            "timeout": data.timeout,
            "status": "active",
            "timer": timer,
            "alert_email": data.alert_email,
            "expires_at": time.time() + data.timeout
        }

    return {"message": f"Monitor {data.id} created with {data.timeout}s timeout"}


# ENDPOINT 2: HEARTBEAT
@app.post("/monitors/{device_id}/heartbeat")
def heartbeat(device_id: str):

    with lock:
        monitor = monitors.get(device_id)

        if not monitor:
            raise HTTPException(status_code=404, detail="Monitor not found")

        # Cancel old timer
        monitor["timer"].cancel()

        # Restart timer
        monitor["timer"] = start_timer(device_id, monitor["timeout"])
        monitor["status"] = "active"
        monitor["expires_at"] = time.time() + monitor["timeout"]

    return {"message": f"Heartbeat received for {device_id}"}


# ENDPOINT 3: PAUSE
@app.post("/monitors/{device_id}/pause")
def pause_monitor(device_id: str):

    with lock:
        monitor = monitors.get(device_id)

        if not monitor:
            raise HTTPException(status_code=404, detail="Monitor not found")

        monitor["timer"].cancel()
        monitor["status"] = "paused"

    return {"message": f"Monitor {device_id} paused"}


# BONUS: GET STATUS
@app.get("/monitors/{device_id}")
def get_status(device_id: str):

    monitor = monitors.get(device_id)

    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")

    return {
        "id": monitor["id"],
        "status": monitor["status"],
        "expires_at": monitor["expires_at"]
    }