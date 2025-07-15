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

# Run for n seconds, print every second
for t in range(4000):
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
