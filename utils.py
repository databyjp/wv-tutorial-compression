import time
import subprocess


def measure_mem_usage(suffix: str):
    print("Measuring memory usage...")
    print("Sleeping for 5 seconds to let the system settle...")
    time.sleep(5)

    command = ["go", "tool", "pprof", "-top", "http://localhost:6060/debug/pprof/heap"]
    with open(f"output/mem_usage_{suffix}.txt", "w") as output_file:
        subprocess.run(command, stdout=output_file, check=True)

    print("Memory usage measured.")
    print(f"Output saved to mem_usage_{suffix}.txt")
