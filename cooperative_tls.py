import traci
import traci.constants as tc
import sumolib

# Cooperative Traffic Signal Control
# Two intersections (A, B) adjusting green times cooperatively

# Parameters
iterations = 5  # number of cooperative learning iterations
green_times = {"A": 20, "B": 20}  # initial green times (sec)
yellow_time = 3


def get_average_waiting_time(intersection_edges):
    total_wait = 0
    count = 0
    for edge in intersection_edges:
        for veh in traci.edge.getLastStepVehicleIDs(edge):
            total_wait += traci.vehicle.getWaitingTime(veh)
            count += 1
    return total_wait / count if count else 0

def cooperative_update(green_A, green_B, wait_A, wait_B):
    # Simple cooperative adjustment (both reduce difference)
    total_wait = wait_A + wait_B
    factor = 1 - 0.1 * ((wait_A - wait_B) / total_wait)
    new_A = max(10, min(30, green_A * factor))
    new_B = max(10, min(30, green_B / factor))
    return new_A, new_B

sumoBinary = "sumo-gui"
sumoCmd = [sumoBinary, "-c", "config.sumocfg"]


print("\nFinal cooperative green splits:")
print(green_times)
