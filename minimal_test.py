import os
import sys
import traci

def minimal_test():
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        print("Please set SUMO_HOME")
        return

    # Create a very simple route file on the fly
    with open('minimal_routes.rou.xml', 'w') as f:
        f.write('''<routes>
    <vType id="car" length="5"/>
    <route id="r1" edges="west_in A_to_B B_to_east2"/>
    <vehicle id="v0" type="car" route="r1" depart="0"/>
</routes>''')

    sumoCmd = ["sumo-gui", "-n", "network.net.xml", "-r", "minimal_routes.rou.xml", "--start"]
    
    try:
        traci.start(sumoCmd)
        print("SUMO started!")
        
        for step in range(100):
            traci.simulationStep()
            if step % 10 == 0:
                print(f"Step {step}, Vehicles: {traci.vehicle.getIDCount()}")
                
        traci.close()
        print("Success!")

        traci.close()
        print("Success!")
        

if __name__ == "__main__":
    minimal_test()