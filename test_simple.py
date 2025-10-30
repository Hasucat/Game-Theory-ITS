import os
import sys
import traci

def test_simulation():
    # Set SUMO path
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        print("❌ Please set SUMO_HOME environment variable")
        return

    sumoBinary = "sumo-gui"  # Try with GUI first to see errors
    config_file = "config.sumocfg"
    
    # Check if files exist
    if not os.path.exists(config_file):
        print(f"❌ Config file {config_file} not found!")
        return
    
    if not os.path.exists("network.net.xml"):
        print("❌ network.net.xml not found!")
        return
        
    if not os.path.exists("routes.rou.xml"):
        print("❌ routes.rou.xml not found!")
        return

    print("✅ All files found")
    
    try:
        sumoCmd = [sumoBinary, "-c", config_file, "--start"]
        traci.start(sumoCmd)
        print("✅ SUMO started successfully")
        
        # Try a few simulation steps
        for step in range(10):
            traci.simulationStep()
            print(f"Step {step}: Simulation running...")
            
        traci.close()
        print("✅ Simulation completed successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simulation()