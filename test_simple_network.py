import os
import sys
import traci

def test_simple_network():
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        print("❌ Please set SUMO_HOME environment variable")
        return

    sumoBinary = "sumo-gui"
    config_file = "simple_config.sumocfg"
    
    if not os.path.exists(config_file):
        print(f"❌ Config file {config_file} not found!")
        return
        
    if not os.path.exists("simple_network.net.xml"):
        print("❌ Network file not found!")
        return

    print("✅ Starting SUMO with simple network...")
    
    try:
        sumoCmd = [sumoBinary, "-c", config_file, "--start"]
        traci.start(sumoCmd)
        print("✅ SUMO started successfully")
        
        # Check available edges
        all_edges = traci.edge.getIDList()
        print(f"✅ Available edges: {all_edges}")
        
        # Check traffic lights
        tls_list = traci.trafficlight.getIDList()
        print(f"✅ Traffic lights: {tls_list}")
        
        # Set simple traffic light states
        if "A" in tls_list:
            traci.trafficlight.setRedYellowGreenState("A", "GGGrrrrrr")
            print("✅ Set traffic light A")
            
        if "B" in tls_list:
            traci.trafficlight.setRedYellowGreenState("B", "GGGrrrrrr") 
            print("✅ Set traffic light B")
        
        # Run simulation
        step = 0
        max_steps = 300
        
        while step < max_steps:
            traci.simulationStep()
            
            # Print progress
            if step % 30 == 0:
                vehicles = traci.vehicle.getIDCount()
                print(f"Step {step}: {vehicles} vehicles")
                
            step += 1

        print("✅ Simulation completed successfully!")
        traci.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_network()