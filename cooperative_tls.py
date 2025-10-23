import traci
import traci.constants as tc
import sumolib

# Cooperative Traffic Signal Control
# Two intersections (A, B) adjusting green times cooperatively

# Parameters
iterations = 5  # number of cooperative learning iterations
green_times = {"A": 20, "B": 20}  # initial green times (sec)
yellow_time = 3

def set_tls(program_id, green):
    """Set a simple green-red cycle"""
    logic = traci.trafficlight.Logic(program_id, 0, 0, [
        traci.trafficlight.Phase(green, "GGrr", 0),
        traci.trafficlight.Phase(yellow_time, "yyrr", 0),
        traci.trafficlight.Phase(40 - green - yellow_time, "rrGG", 0),
        traci.trafficlight.Phase(yellow_time, "rryy", 0)
    ])
    traci.trafficlight.setCompleteRedYellowGreenDefinition(program_id, logic)

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

for i in range(iterations):
    print(f"\n=== Iteration {i+1} ===")
    traci.start(sumoCmd)

    set_tls("A", green_times["A"])
    set_tls("B", green_times["B"])

    step = 0
    while step < 200:
        traci.simulationStep()
        step += 1

    wait_A = get_average_waiting_time(["A_East", "A_West"])
    wait_B = get_average_waiting_time(["B_East", "B_West"])
    print(f"Avg waiting: A={wait_A:.2f}, B={wait_B:.2f}")

    new_A, new_B = cooperative_update(green_times["A"], green_times["B"], wait_A, wait_B)
    green_times["A"], green_times["B"] = new_A, new_B

    traci.close()

print("\nFinal cooperative green splits:")
print(green_times)
