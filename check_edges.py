import sumolib

# Load the network
net = sumolib.net.readNet('network.net.xml')

# Print all edges
print("=== ALL EDGES IN NETWORK ===")
for edge in net.getEdges():
    print(f"Edge: {edge.getID()}, From: {edge.getFromNode().getID()}, To: {edge.getToNode().getID()}")

print("\n=== EDGES THAT CAN BE USED IN ROUTES ===")
# Only regular edges (not internal ones)
for edge in net.getEdges():
    if not edge.isSpecial():
        print(f"Edge: {edge.getID()}")