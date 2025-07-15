import traci
import math
import time




# Define the tracking points (junctions with circles)
tracking_points = [
    (1152.42,1127.79, 50.0, "FP_A"),
    (950.87,810.02, 50.0, "FP_B"),
    (1223.24,631.01, 50.0, "FP_C"),
    (1432.75,948.52, 50.0, "FP_D"),
    (1740.61,719.02, 50.0, "KR_Circle"),
    (766.83,538.53, 50.0, "KG_Road"),

    (1101.36,389.54, 75.0, "District_Office"),
    (383.71,1249.29, 50.0, "Anand_Rao_Jnc"),
    (1176.84,1667.69, 70.0, "Race_Course_Jnc"),
    (1836.39,1677.60, 50.0, "Palace_Road_Jnc")

]
path =  r"C:\Users\USER\projects\TMPv2\sumo\Race_Course 1.0\2025-04-22-17-42-06\osm.sumocfg"

# Start SUMO
traci.start(["sumo-gui", "-c",path, "--start"])
time.sleep(2)


# Draw blue detection circles at each junction
circle_color = (0, 0, 255, 100)
for idx, (xc, yc, r, name) in enumerate(tracking_points):
    pts = [(xc + r * math.cos(a), yc + r * math.sin(a)) for a in [i * (math.pi / 10) for i in range(21)]]
    traci.polygon.add(f"circle_{idx}", pts, circle_color, fill=True, layer=1)  # blue circle
    traci.polygon.setLineWidth(f"circle_{idx}", 2.0)  # thin outline

# Helper function: Check if an edge lies under a circle
def edge_under_circle(edge_id, xc, yc, r):
    from_j = traci.edge.getFromJunction(edge_id)
    to_j = traci.edge.getToJunction(edge_id)
    xf, yf = traci.junction.getPosition(from_j)
    xt, yt = traci.junction.getPosition(to_j)
    return ((xf - xc) ** 2 + (yf - yc) ** 2 <= r ** 2) or ((xt - xc) ** 2 + (yt - yc) ** 2 <= r ** 2)

# Cache: edges per junction
junction_edges_map = {name: [] for _, _, _, name in tracking_points}
for edge_id in traci.edge.getIDList():
    for x, y, radius, name in tracking_points:
        if edge_under_circle(edge_id, x, y, radius):
            junction_edges_map[name].append(edge_id)

# Function to calculate queue length percentage
def get_queue_length_percentage(edge_id):
    try:
        queue_length = traci.edge.getLastStepVehicleNumber(edge_id)
        lane_id = edge_id + "_0"
        total_length = traci.lane.getLength(lane_id)
        return (queue_length / total_length) * 100 if total_length > 0 else 0
    except:
        return 0

# Print header row for queue lengths
headers = [name for _, _, _, name in tracking_points]
print("Time\t" + "\t".join(headers))

# Visualization: For each edge under each circle, draw its shape in red
red = (255, 0, 0, 255)  # Red color for edge polygons
for idx, (xc, yc, r, name) in enumerate(tracking_points):
    for edge_id in traci.edge.getIDList():
        if edge_under_circle(edge_id, xc, yc, r):
            try:
                # Retrieve the edge’s geometry via its first lane
                lanes = traci.edge.getLaneNumber(edge_id)
                lane0 = f"{edge_id}_0"
                shape = traci.lane.getShape(lane0)
                # Draw a red unfilled polygon along the edge's shape
                pid = f"edge_{idx}_{edge_id}"
                traci.polygon.add(pid, shape, red, fill=False, layer=2)  # Red polygon, no fill
                traci.polygon.setLineWidth(pid, 4.0)  # Thick line for the edge
            except Exception as e:
                print(f"Error adding polygon for edge {edge_id}: {e}")
                continue

# Run simulation for 400 seconds, printing queue length percentages
for t in range(400):
    traci.simulationStep()

    row = []
    for name in headers:
        edges = junction_edges_map[name]
        total_pct = 0
        count = 0
        for edge_id in edges:
            pct = get_queue_length_percentage(edge_id)
            total_pct += pct
            count += 1
        avg = total_pct / count if count > 0 else 0
        row.append(f"{avg:.2f}")

    print(f"{t}\t" + "\t".join(row))

# Close the simulation
traci.close()
