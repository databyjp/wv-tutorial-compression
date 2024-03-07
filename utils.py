import time
import subprocess
from pathlib import Path
import re
import json


def measure_mem_usage(suffix: str):
    print("Measuring memory usage...")
    print("Sleeping for 5 seconds to let the system settle...")
    time.sleep(5)

    command = ["go", "tool", "pprof", "-top", "http://localhost:6060/debug/pprof/heap"]
    with open(f"output/mem_usage_{suffix}.txt", "w") as output_file:
        subprocess.run(command, stdout=output_file, check=True)

    print("Memory usage measured.")
    print(f"Output saved to mem_usage_{suffix}.txt")


def parse_results_text():
    output_dir = Path("output")
    output_files = output_dir.glob("*.txt")

    test_outputs = list()
    for f in output_files:
        print(f"Processing {f}...")
        txt = f.read_text()
        # Find the memory footprint in "of 624.83MB total" type pattern
        match = re.search(r"of (\d+\.\d+)MB total", txt)
        if match:
            mem_usage = float(match.group(1))
        else:
            print(f"Could not find memory usage in {f}")
            mem_usage = None

        fname_split = f.name.split("_")
        result = {
            "index_type": fname_split[2],
            "compression": fname_split[3],
            "object_count": int(fname_split[4].split(".")[0]),
            "memory_usage": mem_usage,
        }
        test_outputs.append(result)

        print("Done.")

    with open("test_outputs.json", "w") as f:
        json.dump(test_outputs, f, indent=2)

    return True


def restart_weaviate():
    print("Restarting Weaviate...")
    subprocess.run("docker-compose down", shell=True, check=True)
    subprocess.run("docker-compose up -d", shell=True, check=True)
    print("Sleeping for 5 seconds to let Weaviate spin up...")
    time.sleep(10)
