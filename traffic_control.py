import os
import sys
import traci

def check_edges_exist():
    """Check if the edges we want to use actually exist"""
    try:
        # Get all edge IDs from SUMO
        all_edges = traci.edge.getIDList()
        print("Available edges:", all_edges)
        
        # Check our required edges
        required_edges = ["west_in", "A_to_B", "B_to_east2"]
        for edge in required_edges:
            if edge in all_edges:
                print(f"✅ Edge '{edge}' exists")
            else:
                print(f"❌ Edge '{edge}' NOT FOUND")
                
        return all(edge in all_edges for edge in required_edges)
    except Exception as e:
        print(f"Error checking edges: {e}")
        return False

def set_tls_phases():
    """Set simple traffic light phases"""
    try:
        # For intersection A
        traci.trafficlight.setRedYellowGreenState("A", "GGGrrrrrr")  # Main flow green
        print("✅ Set traffic light A")
        
        # For intersection B  
        traci.trafficlight.setRedYellowGreenState("B", "GGGrrrrrr")  # Main flow green
        print("✅ Set traffic light B")
        
    except Exception as e:
        print(f"Error setting TLS: {e}")

def run_simulation():
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        print("❌ Please set SUMO_HOME environment variable")
        return

    sumoBinary = "sumo-gui"
    config_file = "config.sumocfg"
    
    if not os.path.exists(config_file):
        print(f"❌ Config file {config_file} not found!")
        return

    print("✅ Starting SUMO...")
    
    try:
        sumoCmd = [sumoBinary, "-c", config_file, "--start"]
        traci.start(sumoCmd)
        print("✅ SUMO started successfully")
        
        # Check if our edges exist
        if not check_edges_exist():
            print("❌ Missing required edges!")
            traci.close()
            return
            
        # Set initial traffic light states
        set_tls_phases()
        
        # Run simulation
        step = 0
        max_steps = 200
        
        while step < max_steps:
            traci.simulationStep()
            
            # Print vehicle count every 20 steps
            if step % 20 == 0:
                vehicle_count = traci.vehicle.getIDCount()
                print(f"Step {step}: {vehicle_count} vehicles in network")
                
            step += 1

        print("✅ Simulation completed successfully")
        traci.close()
        
    except Exception as e:
        print(f"❌ Error during simulation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_simulation()