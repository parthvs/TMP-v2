import traci
import math
import time

# Start SUMO
traci.start(["sumo-gui", "-c", "test.sumocfg", "--start"])
time.sleep(2)

tracking_points = [
    (590.85, 1079.43, 50.0, "Junction 1"),
    (1566.25, 1260.03, 50.0, "Big Roundabout"),
    (1043.77, 1175.63, 50.0, "Junction 2"),
    (771.77, 1354.39, 50.0, "Junction 3"),
    (971.33, 1673.16, 50.0, "Junction 4"),
    (1245.12, 1491.37, 50.0, "Junction 5")
]

def is_edge_inside_circle(edge_id, x_center, y_center, radius):
    try:
        from_junc = traci.edge.getFromJunction(edge_id)
        to_junc = traci.edge.getToJunction(edge_id)
        x_from, y_from = traci.junction.getPosition(from_junc)
        x_to, y_to = traci.junction.getPosition(to_junc)
        return (
            math.hypot(x_from - x_center, y_from - y_center) <= radius or
            math.hypot(x_to - x_center, y_to - y_center) <= radius
        )
    except:
        return False

# Cache: edges per junction
junction_edges_map = {name: [] for _, _, _, name in tracking_points}
for edge_id in traci.edge.getIDList():
    for x, y, radius, name in tracking_points:
        if is_edge_inside_circle(edge_id, x, y, radius):
            junction_edges_map[name].append(edge_id)

def get_queue_length_percentage(edge_id):
    try:
        queue_length = traci.edge.getLastStepVehicleNumber(edge_id)
        lane_id = edge_id + "_0"
        total_length = traci.lane.getLength(lane_id)
        return (queue_length / total_length) * 100 if total_length > 0 else 0
    except:
        return 0

# Print header row
headers = [name for _, _, _, name in tracking_points]
print("Time\t" + "\t".join(headers))

# Run for 400 seconds, print every second
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

traci.close()
