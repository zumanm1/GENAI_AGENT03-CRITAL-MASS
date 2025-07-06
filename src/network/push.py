from typing import Dict, List

from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_config, netmiko_save_config
from nornir_napalm.plugins.tasks import napalm_configure
from nornir.core.task import Task, Result

from .retrieve import _build_inventory, LAB_DEVICES


def push_config(config_lines: List[str], host_ports: Dict[str, int] = None, method: str = "netmiko"):
    """Push configuration to devices using chosen method.

    Args:
        config_lines: list of CLI lines to push
        host_ports: mapping of host -> port (default all lab devices)
        method: 'netmiko' or 'napalm'
    Returns dict of host -> status/result str
    """
    if host_ports is None:
        host_ports = LAB_DEVICES

    inventory = _build_inventory(host_ports)
    nr = InitNornir(inventory=inventory, logging={'enabled': False})

    def _netmiko(task: Task):
        r = task.run(netmiko_send_config, config_commands=config_lines)
        task.run(netmiko_save_config)
        return Result(host=task.host, result=r.result)

    def _napalm(task: Task):
        cfg = "\n".join(config_lines)
        r = task.run(napalm_configure, configuration=cfg)
        return Result(host=task.host, result=r.result)

    runner = _napalm if method == "napalm" else _netmiko
    results = nr.run(task=runner)
    return {h: res.result for h, res in results.items()}
