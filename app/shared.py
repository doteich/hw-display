import threading
from datetime import datetime

last_update = datetime.now()

hardwareData = {
    "cpu_temp": 0,
    "cpu_power": 0,
    "cpu_load": 0,
    "gpu_temp": 0,
    "gpu_power": 0,
    "gpu_load": 0,
    "mem_used": 0,
    "gpu_mem_used": 0
}

lock = threading.Lock()
