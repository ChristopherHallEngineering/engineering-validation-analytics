"""Transparent, synthetic engineering verification analysis."""
import csv
import math
import statistics
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Summary:
    count: int
    mean: float
    stdev: float
    minimum: float
    maximum: float
    lower_95: float
    upper_95: float
    failures: int
    all_within_limits: bool

def summarize(values, lower_limit, upper_limit):
    data = [float(v) for v in values]
    if len(data) < 2:
        raise ValueError("At least two observations required")
    if not all(math.isfinite(x) for x in data):
        raise ValueError("Measurements must be finite")
    if not lower_limit < upper_limit:
        raise ValueError("Lower limit must be less than upper limit")
    mu = statistics.mean(data)
    sd = statistics.stdev(data)
    margin = 1.96 * sd / math.sqrt(len(data))
    failed = sum(not (lower_limit <= x <= upper_limit) for x in data)
    return Summary(len(data), mu, sd, min(data), max(data), mu-margin, mu+margin, failed, failed == 0)

def main():
    folder = Path(__file__).parent
    with (folder / "sample_measurements.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    groups = {}
    for row in rows:
        key = row["test_group"]
        entry = groups.setdefault(key, {"values": [], "lower": float(row["lower_limit"]), "upper": float(row["upper_limit"])})
        if (entry["lower"], entry["upper"]) != (float(row["lower_limit"]), float(row["upper_limit"])):
            raise ValueError("Inconsistent acceptance limits within a test group")
        entry["values"].append(float(row["measurement"]))
    with (folder / "validation_report.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["test_group","n","mean","sample_stdev","min","max","normal_approx_ci95_lower","normal_approx_ci95_upper","observations_outside_limits","all_observations_within_limits"])
        for name, group in sorted(groups.items()):
            s = summarize(group["values"],group["lower"],group["upper"])
            writer.writerow([name,s.count,*[round(x,5) for x in (s.mean,s.stdev,s.minimum,s.maximum,s.lower_95,s.upper_95)],s.failures,s.all_within_limits])
            print(f"{name}: n={s.count}, mean={s.mean:.3f}, out-of-limit observations={s.failures}")
    print("Wrote validation_report.csv")

if __name__ == "__main__":
    main()
