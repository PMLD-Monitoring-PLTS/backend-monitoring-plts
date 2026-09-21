import generate
import csv_writer
from time import sleep

SIMULATOR_INTERVAL = 30

SCENARIO = "NORMAL"

print(
    f"Simulator PLTS dimulai | "
    f"Scenario: {SCENARIO} | "
    f"Interval: {SIMULATOR_INTERVAL}s"
)

try:
    csv_writer.create_csv()
    while True:

        telemetry = generate.generate_telemetry(SCENARIO)

        csv_writer.append_to_csv(telemetry)

        print(telemetry)

        sleep(SIMULATOR_INTERVAL)

except KeyboardInterrupt:
    print("\nSimulator dihentikan.")