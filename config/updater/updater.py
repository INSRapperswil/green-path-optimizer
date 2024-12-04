import typer
import logging
import p4runtime_lib.simple_controller
import helpers as hlp

from os import path
from nornir import InitNornir
from nornir.core.task import Task, Result
from nornir_rich.progress_bar import RichProgressBar
from nornir_rich.functions import print_result


def update_bmv2_runtime(task: Task) -> Result:
    dump_file = path.join(
        task.host.get("log_dir"), f"{task.host}-p4runtime-requests.txt"
    )
    runtime_file = path.join(
        task.host.get("bmv2_config_path"),
        task.host.get("runtime_file_name"),
    )

    with open(runtime_file, "r") as f:
        p4runtime_lib.simple_controller.program_switch(
            addr=f"{task.host.get('mininet_host')}:{task.host.get('port')}",
            device_id=task.host.get("device_id"),
            sw_conf_file=f,
            workdir="/home/boss/git/green-path-optimizer",
            proto_dump_fpath=dump_file,
            runtime_json=runtime_file,
        )
    return Result(host=task.host, result="runtime configuration updated", changed=True)


def main(verbose: bool = False):
    nr = InitNornir(config_file=f"config/updater/config.yaml", dry_run=False)

    # Retrieve the checksums of the previous run on the same host and inventory
    nr.inventory.defaults.data["previous_run_checksums"] = hlp.read_checksums(
        nr.inventory.defaults.data.get("checksum_file"),
        nr.inventory.defaults.data.get("mininet_host"),
        nr.config.inventory.options.get("host_file"),
    )

    # Get a list of all runtime configurations based on the target inventory
    runtime_files = [
        path.join(
            nr.inventory.defaults.data.get("bmv2_config_path"),
            host[1].data.get("runtime_file_name"),
        )
        for host in nr.inventory.hosts.items()
    ]

    # Calculate the checksums of the current runtime configurations
    nr.inventory.defaults.data["current_run_checksums"] = hlp.calculate_checksums(
        runtime_files
    )

    # Compare the checksums of the current and the previous run for equality (in case there was a previous run)
    if nr.inventory.defaults.data["previous_run_checksums"]:
        if hlp.are_checksums_equal(
            nr.inventory.defaults.data["previous_run_checksums"]["checksums"],
            nr.inventory.defaults.data["current_run_checksums"]["checksums"],
        ):
            print(
                f"The runtime configurations were not modified since the previous run at {nr.inventory.defaults.data['previous_run_checksums']['timestamp']} on {nr.inventory.defaults.data.get('mininet_host')}."
            )
            decision = input("Do you want to push the configurations anyway? [Y/n]: ")
            if decision.lower() != "y" and decision != "":
                print("Task execution cancelled.")
                exit()

    nr_with_processors = nr.with_processors([RichProgressBar()])
    result = nr_with_processors.run(task=update_bmv2_runtime)

    # Persist the checksums of the current run by patching the file with the new or updated content
    hlp.write_checksums(
        nr.inventory.defaults.data.get("checksum_file"),
        nr.inventory.defaults.data.get("mininet_host"),
        nr.config.inventory.options.get("host_file"),
        nr.inventory.defaults.data["current_run_checksums"],
    )

    log_level = logging.INFO if verbose else logging.ERROR
    print_result(
        result,
        vars=["result", "failed", "diff", "changed", "severity_level"],
        severity_level=log_level,
    )


if __name__ == "__main__":
    typer.run(main)
