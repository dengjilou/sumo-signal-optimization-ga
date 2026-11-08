"""Compare fixed signal splits on the same SUMO network and demand."""

from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
SIGNAL = "J1"
APPROACHES = ("E2W", "W2E", "N2S", "S2N")
BASELINE = (26, 26, 26, 26)
AMBER = 3
ALL_RED = 1
TRAIN_SEED = 42
DEMANDS = {"1x": "routes_final.rou.xml", "5x": "routes_5x.rou.xml"}


def write_program(path, greens):
    """Give one approach a green at a time. Keep the cycle at 120 seconds."""
    if len(greens) != 4 or min(greens) < 12 or sum(greens) != sum(BASELINE):
        raise ValueError("Expected four greens of at least 12 s totalling 104 s")
    network = ET.parse(CONFIG / "changjiang.net.xml")
    indices = {int(link.attrib["linkIndex"]): link.attrib["from"].split("_")[0]
               for link in network.findall(f"connection[@tl='{SIGNAL}']")}
    approaches = [indices[i] for i in range(len(indices))]
    if set(approaches) != set(APPROACHES):
        raise ValueError("Unexpected J1 approach IDs")

    additional = ET.Element("additional")
    logic = ET.SubElement(additional, "tlLogic", id=SIGNAL, type="static",
                          programID="approach_split", offset="0")
    for approach, green in zip(APPROACHES, greens):
        for duration, active in ((green, "G"), (AMBER, "y"), (ALL_RED, "r")):
            state = "".join(active if item == approach else "r" for item in approaches)
            ET.SubElement(logic, "phase", duration=str(duration), state=state)
    ET.indent(additional)
    ET.ElementTree(additional).write(path, encoding="utf-8", xml_declaration=True)


def evaluate(program, routes, seed, duration=3600):
    sumo_home = os.environ.get("SUMO_HOME")
    executable = str(Path(sumo_home) / "bin" / ("sumo.exe" if os.name == "nt" else "sumo")) if sumo_home else "sumo"
    with tempfile.TemporaryDirectory(prefix="changjiang-") as folder:
        tripinfo = Path(folder) / "tripinfo.xml"
        summary = Path(folder) / "summary.xml"
        statistics = Path(folder) / "statistics.xml"
        result = subprocess.run([
            executable, "-c", str(CONFIG / "changjiang.sumocfg"),
            "--route-files", str(CONFIG / routes),
            "--additional-files", str(program),
            "--seed", str(seed), "--end", str(duration), "--collision.check-junctions", "true",
            "--tripinfo-output", str(tripinfo), "--tripinfo-output.write-unfinished", "true",
            "--summary-output", str(summary),
            "--statistic-output", str(statistics),
        ], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())
        trips = ET.parse(tripinfo).findall("tripinfo")
        last = ET.parse(summary).getroot()[-1]
        totals = ET.parse(statistics).getroot()
        if not trips:
            raise RuntimeError("No vehicles departed")
        return {
            "duration_s": duration,
            "arrived": int(last.attrib["arrived"]),
            "running": int(last.attrib["running"]),
            "pending_departure": int(last.attrib["waiting"]),
            "collisions": int(totals.find("safety").attrib["collisions"]),
            "teleports": int(totals.find("teleports").attrib["total"]),
            "mean_wait_s": round(sum(float(t.attrib["waitingTime"]) for t in trips) / len(trips), 3),
            "mean_time_loss_s": round(sum(float(t.attrib["timeLoss"]) for t in trips) / len(trips), 3),
            "mean_depart_delay_s": round(sum(float(t.attrib["departDelay"]) for t in trips) / len(trips), 3),
        }


def main():
    cases = [(seed, demand, label) for seed, demand in
             ((TRAIN_SEED, "1x"), (TRAIN_SEED + 1, "1x"), (TRAIN_SEED, "5x"))
             for label in ("equal", "optimized")]

    def run(case):
        seed, demand, label = case
        return evaluate(CONFIG / f"signal_{label}.add.xml", DEMANDS[demand], seed,
                        duration=1800 if demand == "5x" else 3600)

    with ThreadPoolExecutor(max_workers=3) as pool:
        report = {f"{demand}_seed{seed}_{label}": metrics
                  for (seed, demand, label), metrics in zip(cases, pool.map(run, cases))}
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
