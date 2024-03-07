from pathlib import Path
import re
import json

output_dir = Path("output")
output_files = output_dir.glob("*.txt")

benchmark_outputs = list()
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
        "object_count": int(fname_split[5].split(".")[0]),
        "memory_usage": mem_usage
    }
    benchmark_outputs.append(result)

    print("Done.")

with open("benchmark_outputs.json", "w") as f:
    json.dump(benchmark_outputs, f, indent=2)
