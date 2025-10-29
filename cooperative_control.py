import os
import sys
import traci
import time

class CooperativeTrafficControl:
    def __init__(self):
        self.green_times = {"A": 30, "B": 30}
        self.yellow_time = 3
        self.iteration = 0
        
    def set_traffic_light_phases(self, tls_id, green_time):
        """Set adaptive traffic light phases"""
        try:
            # Define phases for the intersection
            # Phase 0: Main corridor (west->east) green
            # Phase 1: Yellow for main corridor
            # Phase 2: Side streets green
            # Phase 3: Yellow for side streets
            
            if tls_id == "A":
                # For intersection A: west_in, northA_in, southA_in -> A_to_B
                phases = [
                    traci.trafficlight.Phase(green_time, "GGGrrrrrr", 0, 0),  # Main green
                    traci.trafficlight.Phase(self.yellow_time, "yyyrrrrrr", 0, 0),  # Main yellow
                    traci.trafficlight.Phase(green_time, "rrrGGGrrr", 0, 0),  # Side green
                    traci.trafficlight.Phase(self.yellow_time, "rrryyyrrr", 0, 0),  # Side yellow
                ]
            else:  # Intersection B
                # For intersection B: A_to_B, northB_in, southB_in -> B_to_east
                phases = [
                    traci.trafficlight.Phase(green_time, "GGGrrrrrr", 0, 0),  # Main green
                    traci.trafficlight.Phase(self.yellow_time, "yyyrrrrrr", 0, 0),  # Main yellow
                    traci.trafficlight.Phase(green_time, "rrrGGGrrr", 0, 0),  # Side green
                    traci.trafficlight.Phase(self.yellow_time, "rrryyyrrr", 0, 0),  # Side yellow
                ]
            
            logic = traci.trafficlight.Logic(
                programID=f"cooperative_{tls_id}",
                type=0,
                currentPhaseIndex=0,
                phases=phases
            )
            
            traci.trafficlight.setCompleteRedYellowGreenDefinition(tls_id, logic)
            traci.trafficlight.setProgram(tls_id, f"cooperative_{tls_id}")
            print(f"✅ {tls_id}: Green time = {green_time}s")
            
        except Exception as e:
            print(f"❌ Error setting TLS {tls_id}: {e}")

    def get_intersection_waiting_time(self, tls_id):
        """Calculate average waiting time for vehicles at intersection"""
        try:
            total_wait = 0
            vehicle_count = 0
            
            # Get controlled lanes for this traffic light
            controlled_lanes = traci.trafficlight.getControlledLanes(tls_id)
            
            for lane in controlled_lanes:
                vehicles = traci.lane.getLastStepVehicleIDs(lane)
                for vehicle in vehicles:
                    speed = traci.vehicle.getSpeed(vehicle)
                    if speed < 0.1:  # Vehicle is stopped or very slow
                        wait_time = traci.vehicle.getWaitingTime(vehicle)
                        total_wait += wait_time
                        vehicle_count += 1
            
            return total_wait / vehicle_count if vehicle_count > 0 else 0
            
        except Exception as e:
            print(f"❌ Error calculating waiting time for {tls_id}: {e}")
            return 0

    def get_intersection_vehicle_count(self, tls_id):
        """Count vehicles approaching the intersection"""
        try:
            vehicle_count = 0
            controlled_lanes = traci.trafficlight.getControlledLanes(tls_id)
            
            for lane in controlled_lanes:
                vehicle_count += traci.lane.getLastStepVehicleNumber(lane)
                
            return vehicle_count
        except Exception as e:
            print(f"❌ Error counting vehicles for {tls_id}: {e}")
            return 0

    def cooperative_decision(self, wait_A, wait_B, vehicles_A, vehicles_B):
        """Make cooperative decision to adjust green times"""
        # Simple cooperative algorithm
        total_wait = wait_A + wait_B
        total_vehicles = vehicles_A + vehicles_B
        
        if total_wait == 0 and total_vehicles == 0:
            return self.green_times["A"], self.green_times["B"]
        
        # Adjust based on both waiting time and vehicle count
        demand_A = (wait_A + vehicles_A * 2) / 10
        demand_B = (wait_B + vehicles_B * 2) / 10
        
        total_demand = demand_A + demand_B
        
        if total_demand > 0:
            # Distribute green time proportionally to demand
            new_A = max(20, min(50, 30 * (demand_A / total_demand) * 2))
            new_B = max(20, min(50, 30 * (demand_B / total_demand) * 2))
            
            # Smooth the transition
            smooth_A = 0.7 * self.green_times["A"] + 0.3 * new_A
            smooth_B = 0.7 * self.green_times["B"] + 0.3 * new_B
            
            return smooth_A, smooth_B
        else:
            return self.green_times["A"], self.green_times["B"]

    def run_iteration(self):
        """Run one iteration of cooperative control"""
        self.iteration += 1
        print(f"\n🔄 === Cooperative Control Iteration {self.iteration} ===")
        
        # Set initial traffic light programs
        self.set_traffic_light_phases("A", self.green_times["A"])
        self.set_traffic_light_phases("B", self.green_times["B"])
        
        # Run simulation for evaluation period
        evaluation_steps = 300  # 300 seconds
        step = 0
        
        wait_times_A = []
        wait_times_B = []
        vehicle_counts_A = []
        vehicle_counts_B = []
        
        while step < evaluation_steps:
            traci.simulationStep()
            
            # Collect metrics every 10 seconds
            if step % 10 == 0:
                wait_A = self.get_intersection_waiting_time("A")
                wait_B = self.get_intersection_waiting_time("B")
                vehicles_A = self.get_intersection_vehicle_count("A")
                vehicles_B = self.get_intersection_vehicle_count("B")
                
                wait_times_A.append(wait_A)
                wait_times_B.append(wait_B)
                vehicle_counts_A.append(vehicles_A)
                vehicle_counts_B.append(vehicles_B)
                
                if step % 30 == 0:
                    print(f"⏱️ Step {step}: A(wait:{wait_A:.1f}s, vehicles:{vehicles_A}) | B(wait:{wait_B:.1f}s, vehicles:{vehicles_B})")
            
            step += 1
        
        # Calculate averages
        avg_wait_A = sum(wait_times_A) / len(wait_times_A) if wait_times_A else 0
        avg_wait_B = sum(wait_times_B) / len(wait_times_B) if wait_times_B else 0
        avg_vehicles_A = sum(vehicle_counts_A) / len(vehicle_counts_A) if vehicle_counts_A else 0
        avg_vehicles_B = sum(vehicle_counts_B) / len(vehicle_counts_B) if vehicle_counts_B else 0
        
        print(f"📊 Averages - A: {avg_wait_A:.1f}s wait, {avg_vehicles_A:.1f} vehicles | B: {avg_wait_B:.1f}s wait, {avg_vehicles_B:.1f} vehicles")
        
        # Make cooperative decision
        new_A, new_B = self.cooperative_decision(avg_wait_A, avg_wait_B, avg_vehicles_A, avg_vehicles_B)
        
        print(f"🔄 Adjusting: A {self.green_times['A']:.1f}s → {new_A:.1f}s | B {self.green_times['B']:.1f}s → {new_B:.1f}s")
        
        self.green_times["A"] = new_A
        self.green_times["B"] = new_B
        
        return avg_wait_A + avg_wait_B  # Return total waiting time for stopping condition

def main():
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        print("❌ Please set SUMO_HOME environment variable")
        return

    sumoBinary = "sumo-gui"
    config_file = "generated_config.sumocfg"
    
    if not os.path.exists(config_file):
        print("❌ Config file not found!")
        return

    # Create controller
    controller = CooperativeTrafficControl()
    
    print("🚦 Starting Cooperative Traffic Signal Control")
    print("=============================================")
    
    try:
        # Start SUMO
        sumoCmd = [sumoBinary, "-c", config_file, "--start"]
        traci.start(sumoCmd)
        
        print("✅ SUMO started successfully!")
        print(f"✅ Traffic lights: {traci.trafficlight.getIDList()}")
        print(f"✅ Edges: {len(traci.edge.getIDList())} edges loaded")
        
        # Run multiple iterations of cooperative control
        max_iterations = 5
        min_improvement = 0.1  # Stop if improvement is less than 10%
        
        previous_total_wait = float('inf')
        
        for iteration in range(max_iterations):
            total_wait = controller.run_iteration()
            
            # Check for convergence
            if previous_total_wait != float('inf'):
                improvement = (previous_total_wait - total_wait) / previous_total_wait
                print(f"📈 Improvement: {improvement:.1%}")
                
                if improvement < min_improvement and improvement > 0:
                    print("🎯 Convergence reached! Stopping optimization.")
                    break
            
            previous_total_wait = total_wait
        
        print("\n🎊 Cooperative Control Completed!")
        print("=================================")
        print(f"Final green times:")
        print(f"🚦 Intersection A: {controller.green_times['A']:.1f} seconds")
        print(f"🚦 Intersection B: {controller.green_times['B']:.1f} seconds")
        print(f"Total iterations: {controller.iteration}")
        
        # Keep simulation running to observe final configuration
        print("\n👀 Observing final configuration... (Press Ctrl+C to stop)")
        while True:
            traci.simulationStep()
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Simulation stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        traci.close()
        print("✅ Simulation closed")

if __name__ == "__main__":
    main()