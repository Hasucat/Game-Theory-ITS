import os
import sys
import traci

def test_generated_network():
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        print("❌ Please set SUMO_HOME environment variable")
        return

    # Check if files exist
    if not os.path.exists("generated_network.net.xml"):
        print("❌ Generated network not found! Run create_network.py first")
        return
        
    if not os.path.exists("generated_config.sumocfg"):
        print("❌ Config file not found!")
        return

    sumoBinary = "sumo-gui"
    config_file = "generated_config.sumocfg"

    print("✅ Testing generated network...")
    
    try:
        sumoCmd = [sumoBinary, "-c", config_file, "--start"]
        traci.start(sumoCmd)
        print("✅ SUMO started successfully!")
        
        # Check what we have
        edges = traci.edge.getIDList()
        print(f"✅ Found {len(edges)} edges: {edges}")
        
        tls = traci.trafficlight.getIDList() 
        print(f"✅ Traffic lights: {tls}")
        
        # Run simulation
        for step in range(200):
            traci.simulationStep()
            if step % 20 == 0:
                vehicles = traci.vehicle.getIDCount()
                print(f"Step {step}: {vehicles} vehicles")
                
        print("✅ Simulation completed!")
        traci.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_generated_network()