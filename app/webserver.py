# global vars
from flask import Flask, request, Response
from datetime import datetime
import shared


filterArray = [
    {
        "hardwareType": "Cpu",
        "sensorType": "Load",
        "sensorName": "CPU Total",
        "var": "cpu_load",
    },
    {
        "hardwareType": "Memory",
        "sensorType": "Data",
        "sensorName": "Memory Used",
        "var": "mem_used",
    },
    {
        "hardwareType": "Cpu",
        "sensorType": "Temperature",
        "sensorName": "Core (Tctl/Tdie)",
        "var": "cpu_temp",
    },
    {
        "hardwareType": "GpuNvidia",
        "sensorType": "Temperature",
        "sensorName": "GPU Core",
        "var": "gpu_temp",
    },
    {
        "hardwareType": "GpuNvidia",
        "sensorType": "SmallData",
        "sensorName": "GPU Memory Used",
        "var": "gpu_mem_used",
    },
    {
        "hardwareType": "GpuNvidia",
        "sensorType": "Load",
        "sensorName": "GPU Core",
        "var": "gpu_load",
    }
]


app = Flask(__name__)


@app.route("/stats", methods=["POST"])
def update_data():

    data = request.get_json()
    # for set in data:
    # print(set["hardwareName"], set["hardwareType"],
    #       set["sensorName"], set["sensorType"], set["value"])

    with shared.lock:
        shared.last_update = datetime.now()


    for filter in filterArray:
        for set in data:
            if set["hardwareType"] == filter["hardwareType"] and set["sensorType"] == filter["sensorType"] and set["sensorName"] == filter["sensorName"]:

                with shared.lock:
                    shared.hardwareData[filter["var"]] = set["value"]

    return Response(status=200)


@app.route("/", methods=["GET"])
def root():
    return Response(status=200)


def run_flask_server():
    # 'use_reloader=False' is crucial here!
    # Without it, Flask might start a secondary process and confuse the threads.
    print("--- Web Server Running on Port 8080 ---")
    app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)
