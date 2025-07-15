import traci
import math
import time

# Start SUMO
traci.start(["sumo-gui", "-c", "test.sumocfg", "--start"])
time.sleep(2)  # Allow SUMO to initialize

# Tracking Locations (x, y, radius, name)
tracking_points = [
    (590.85, 1079.43, 50.0, "Junction 1"),
    (1566.25, 1260.03, 50.0, "Big Roundabout"),
    (1043.77, 1175.63, 50.0, "Junction 2"),
    (771.77, 1354.39, 50.0, "Junction 3"),
    (971.33, 1673.16, 50.0, "Junction 4"),
    (1245.12, 1491.37, 50.0, "Junction 5")
]

# Function to check if an edge is inside a detection circle
def is_edge_inside_circle(edge_id, x_center, y_center, radius):
    # Get the node IDs connected by the edge
    from_junc = traci.edge.getFromJunction(edge_id)
    to_junc   = traci.edge.getToJunction(edge_id)

    # Get the positions of the two nodes (start and end of the edge)
    x_from, y_from = traci.junction.getPosition(from_junc)
    x_to, y_to     = traci.junction.getPosition(to_junc)

    # Check if either of the edge's node positions fall inside the circle
    def is_within_circle(x, y):
        return math.sqrt((x - x_center) ** 2 + (y - y_center) ** 2) <= radius

    return is_within_circle(x_from, y_from) or is_within_circle(x_to, y_to)

# Flag to track if we've already printed the edges
edges_printed = set()

# Run simulation for 1 step (just to initialize the simulation)
traci.simulationStep()

# Print edges inside each circle once, at the start
for (x, y, radius, name) in tracking_points:
    print(f"\nEdges within the circle of {name}:")
    for edge_id in traci.edge.getIDList():
        if edge_id not in edges_printed and is_edge_inside_circle(edge_id, x, y, radius):
            print(f"  - {edge_id}")
            edges_printed.add(edge_id)  # Mark this edge as printed

# Close the simulation
traci.close()
