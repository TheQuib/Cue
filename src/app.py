import os
import time
import threading
import logging
import subprocess
from functools import wraps
from flask import Flask, jsonify, request

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

app = Flask(__name__)

cec_process = None
cec_lock = threading.Lock()
cec_status = {
    "running": False,
    "bus_ready": False,
    "phys_addr": None
}


def load_config():
    import yaml
    config_path = os.environ.get("CONFIG_PATH", "/app/config.yml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        config = load_config()
        expected_key = config.get("api_key")

        if not expected_key:
            log.warning("No api_key set in config - endpoint is unprotected")
            return f(*args, **kwargs)

        provided_key = request.headers.get("X-API-Key")
        if not provided_key or provided_key != expected_key:
            log.warning(f"Unauthorized request from {request.remote_addr}")
            return jsonify({"error": "Unauthorized"}), 401

        return f(*args, **kwargs)
    return decorated


def send_cec(command: str):
    with cec_lock:
        if cec_process is None or cec_process.poll() is not None:
            raise RuntimeError("cec-client is not running")
        if not cec_status["bus_ready"]:
            raise RuntimeError("CEC bus not ready - TV may be in deep sleep")
        cec_process.stdin.write(f"{command}\n")
        cec_process.stdin.flush()
        log.info(f"Sent CEC command: {command}")


def tv_on():
    config = load_config()
    content_input = config.get("content_hdmi_port", 1)
    on_delay = config.get("on_delay", 1)
    input_delay = config.get("input_delay", 3)
    content_addr = f"1F:82:{content_input}0:00"

    log.info("TV ON sequence starting...")
    send_cec("on 0")
    time.sleep(on_delay)
    send_cec("as")
    time.sleep(input_delay)
    send_cec(f"tx {content_addr}")
    log.info("TV ON sequence complete")


def tv_off():
    config = load_config()
    off_delay = config.get("off_delay", 2)

    log.info("TV OFF sequence starting...")
    send_cec("as")
    time.sleep(off_delay)
    send_cec("standby 0")
    log.info("TV OFF sequence complete")


def tv_input(port: int):
    addr = f"1F:82:{port}0:00"
    log.info(f"Switching to HDMI {port}...")
    send_cec(f"tx {addr}")


def monitor_cec_output():
    while True:
        if cec_process is None or cec_process.poll() is not None:
            time.sleep(1)
            continue

        try:
            for line in cec_process.stdout:
                line = line.rstrip()
                log.debug(f"[cec-client] {line}")

                if "phys_addr=" in line and "ffff" not in line.lower():
                    cec_status["bus_ready"] = True
                    addr = line.split("phys_addr=")[-1].split()[0]
                    cec_status["phys_addr"] = addr
                    log.info(f"CEC bus ready - physical address: {addr}")

                elif "phys_addr=ffff" in line.lower():
                    cec_status["bus_ready"] = False
                    cec_status["phys_addr"] = "ffff"
                    log.warning("CEC bus lost - TV entered deep sleep")

                elif "power status changed" in line and "to 'on'" in line:
                    cec_status["bus_ready"] = True
                    log.info("TV power status: on - bus ready")

                elif "power status changed" in line and "to 'standby'" in line:
                    log.info("TV power status: standby")

        except Exception as e:
            log.error(f"cec-client monitor error: {e}")

        log.warning("cec-client process ended, restarting in 5 seconds...")
        cec_status["running"] = False
        cec_status["bus_ready"] = False
        time.sleep(5)
        start_cec_client()


def start_cec_client():
    global cec_process

    log.info("Starting cec-client...")
    try:
        cec_process = subprocess.Popen(
            ["cec-client"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        cec_status["running"] = True
        log.info("cec-client started")
    except Exception as e:
        log.error(f"Failed to start cec-client: {e}")
        cec_status["running"] = False
        cec_status["bus_ready"] = False


@app.route("/health", methods=["GET"])
@require_api_key
def health():
    config = load_config()
    return jsonify({
        "status": "ok",
        "tv_id": config.get("tv_id", "unknown"),
        "cec_client": "running" if cec_status["running"] else "stopped",
        "bus_ready": cec_status["bus_ready"],
        "phys_addr": cec_status["phys_addr"]
    })


@app.route("/command", methods=["POST"])
@require_api_key
def command():
    data = request.get_json()
    if not data or "command" not in data:
        return jsonify({"error": "Missing 'command' field"}), 400

    cmd = data["command"]
    log.info(f"Received command: {cmd} from {request.remote_addr}")

    try:
        if cmd == "on":
            threading.Thread(target=tv_on).start()
        elif cmd == "off":
            threading.Thread(target=tv_off).start()
        elif cmd.startswith("input_hdmi"):
            port = int(cmd[-1])
            threading.Thread(target=tv_input, args=(port,)).start()
        else:
            return jsonify({"error": f"Unknown command: {cmd}"}), 400

        return jsonify({"status": "ok", "command": cmd})

    except RuntimeError as e:
        log.warning(f"Command rejected: {e}")
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        log.error(f"Command failed: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    start_cec_client()

    monitor_thread = threading.Thread(target=monitor_cec_output, daemon=True)
    monitor_thread.start()

    time.sleep(5)

    config = load_config()
    port = config.get("api_port", 5000)
    log.info(f"Starting API on port {port}...")
    app.run(host="0.0.0.0", port=port)
