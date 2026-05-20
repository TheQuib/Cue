import subprocess
import yaml
import os
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

CONFIG_PATH = os.environ.get("CONFIG_PATH", "/app/config.yml")

COMMAND_MAP = {
    "on":          "on 0",
    "standby":     "standby 0",
    "active":      "as",
    "input_hdmi1": "tx 1F:82:10:00",
    "input_hdmi2": "tx 1F:82:20:00",
    "input_hdmi3": "tx 1F:82:30:00",
    "input_hdmi4": "tx 1F:82:40:00",
}


def load_config(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def send_cec(command: str, adapter: str = None) -> None:
    cec_cmd = COMMAND_MAP.get(command)
    if not cec_cmd:
        raise ValueError(f"Unknown CEC command: '{command}'. Valid commands: {list(COMMAND_MAP.keys())}")

    adapter_flag = f" -p {adapter}" if adapter else ""
    full_cmd = f'echo "{cec_cmd}" | cec-client -s -d 1{adapter_flag}'

    log.info(f"Sending CEC command: {cec_cmd}")
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        log.error(f"cec-client error: {result.stderr}")
        sys.exit(1)

    log.info("CEC command sent successfully")


def main():
    config = load_config(CONFIG_PATH)

    # CEC_COMMAND env var overrides config file (used by Ansible/Semaphore)
    command = os.environ.get("CEC_COMMAND") or config.get("cec_command")
    adapter = config.get("cec_adapter", None)

    if not command:
        log.error("No CEC command specified. Set 'cec_command' in config.yml or CEC_COMMAND env var.")
        sys.exit(1)

    log.info(f"TV ID: {config.get('tv_id', 'unknown')} | Command: {command}")
    send_cec(command, adapter)


if __name__ == "__main__":
    main()
