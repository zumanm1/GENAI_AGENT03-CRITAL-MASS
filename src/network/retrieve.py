from typing import Dict, List

from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result

# Telnet connection via netmiko requires setting device_type="cisco_ios_telnet"

DEFAULT_USERNAME = "cisco"
DEFAULT_PASSWORD = "cisco"
DEFAULT_IP = "172.16.39.102"

# Define known lab devices with port mapping
LAB_DEVICES = {
    "R15": 32783,
    "R16": 32773,
    # add more when available
}

def _build_inventory(host_ports: Dict[str, int]):
    """Create an inline Nornir inventory for telnet-accessible routers."""
    hosts = {}
    for hostname, port in host_ports.items():
        hosts[hostname] = {
            "hostname": DEFAULT_IP,
            "port": port,
            "username": DEFAULT_USERNAME,
            "password": DEFAULT_PASSWORD,
            "platform": "cisco_ios",
            "connection_options": {
                "netmiko": {
                    "extras": {
                        "device_type": "cisco_ios_telnet",
                    }
                }
            },
        }
    return {
        "hosts": hosts,
        "groups": {},
        "defaults": {"connection_options": {}}
    }


def _run_commands(task: Task, commands: List[str]):
    """Run given commands and attach outputs."""
    outputs = {}
    for cmd in commands:
        r = task.run(netmiko_send_command, command_string=cmd, use_textfsm=True, strip_command=False)
        outputs[cmd] = r.result
    return Result(host=task.host, result=outputs)


def retrieve_basic_info(host_ports: Dict[str, int] = None, commands: List[str] = None):
    """Connect to devices and retrieve command outputs.

    Returns dict keyed by hostname with nested dict of command -> output.
    """
    if host_ports is None:
        host_ports = LAB_DEVICES
    if commands is None:
        commands = ["show ip int brief", "show version"]

    inventory_dict = _build_inventory(host_ports)
    nr = InitNornir(inventory=inventory_dict, logging={'enabled': False})

    results = nr.run(task=_run_commands, commands=commands)

    output = {}
    for host, multi in results.items():
        # multi.result is dict of cmd->output
        output[host] = multi.result
    return output


if __name__ == "__main__":
    data = retrieve_basic_info()
    print_result(data)
