import subprocess
import os
import sys

def create_network_files():
    """Create basic .nod.xml and .edg.xml files to generate a network"""
    
    # Create nodes file
    with open('simple_nodes.nod.xml', 'w') as f:
        f.write('''<?xml version="1.0" encoding="UTF-8"?>
<nodes>
    <node id="west" x="0" y="50" type="priority"/>
    <node id="A" x="100" y="50" type="traffic_light"/>
    <node id="B" x="250" y="50" type="traffic_light"/> 
    <node id="east" x="400" y="50" type="priority"/>
    <node id="northA" x="100" y="100" type="priority"/>
    <node id="southA" x="100" y="0" type="priority"/>
    <node id="northB" x="250" y="100" type="priority"/>
    <node id="southB" x="250" y="0" type="priority"/>
</nodes>''')

    # Create edges file  
    with open('simple_edges.edg.xml', 'w') as f:
        f.write('''<?xml version="1.0" encoding="UTF-8"?>
<edges>
    <!-- Main corridor -->
    <edge id="west_in" from="west" to="A" numLanes="1" speed="13.9"/>
    <edge id="A_to_B" from="A" to="B" numLanes="1" speed="13.9"/>
    <edge id="B_to_east" from="B" to="east" numLanes="1" speed="13.9"/>

    <!-- Side connections for A -->
    <edge id="northA_in" from="northA" to="A" numLanes="1" speed="10"/>
    <edge id="A_to_northA" from="A" to="northA" numLanes="1" speed="10"/>
    <edge id="southA_in" from="southA" to="A" numLanes="1" speed="10"/>
    <edge id="A_to_southA" from="A" to="southA" numLanes="1" speed="10"/>

    <!-- Side connections for B -->
    <edge id="northB_in" from="northB" to="B" numLanes="1" speed="10"/>
    <edge id="B_to_northB" from="B" to="northB" numLanes="1" speed="10"/>
    <edge id="southB_in" from="southB" to="B" numLanes="1" speed="10"/>
    <edge id="B_to_southB" from="B" to="southB" numLanes="1" speed="10"/>
</edges>''')

    print("✅ Created node and edge files")

def generate_network():
    """Use netconvert to generate the network"""
    try:
        # Use netconvert to create the network
        cmd = [
            'netconvert',
            '--node-files', 'simple_nodes.nod.xml',
            '--edge-files', 'simple_edges.edg.xml', 
            '--output-file', 'generated_network.net.xml',
            '--no-turnarounds'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Successfully generated network: generated_network.net.xml")
            return True
        else:
            print("❌ Error generating network:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running netconvert: {e}")
        return False

if __name__ == "__main__":
    create_network_files()
    if generate_network():
        print("🎉 Network generation completed!")
    else:
        print("💥 Network generation failed!")