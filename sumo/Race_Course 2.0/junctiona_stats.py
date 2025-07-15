import traci
import math
import csv
import time

# GUI mode toggle
gui_mode = "0"
sumo_binary = "sumo"

# Tracking Locations (x, y, radius, name)
tracking_points = [
    (1152.42, 1127.79, 50.0, "FP_A"),
    (950.87, 810.02, 50.0, "FP_B"),
    (1223.24, 631.01, 50.0, "FP_C"),
    (1432.75, 948.52, 50.0, "FP_D"),
    (1740.61, 719.02, 50.0, "KR_Circle"),
    (766.83, 538.53, 50.0, "KG_Road"),
    (1101.36, 389.54, 75.0, "District_Office"),
    (383.71, 1249.29, 50.0, "Anand_Rao_Jnc"),
    (1176.84, 1667.69, 70.0, "Race_Course_Jnc"),
    (1836.39, 1677.60, 70.0, "Palace_Road_Jnc")
]

# Helper: Check if edge is within a tracking point's radius
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

# Helper: Calculate average queue length percent
def get_queue_length_percentage(edge_id):
    try:
        queue_length = traci.edge.getLastStepVehicleNumber(edge_id)
        lane_id = edge_id + "_0"
        total_length = traci.lane.getLength(lane_id)
        return (queue_length / total_length) * 100 if total_length > 0 else 0
    except:
        return 0

def update_traffic_scale(time_step):
    original_scales = [
        0.317, 0.250, 0.226, 0.200, 0.208, 0.243, 0.293, 0.665,
        0.805, 0.876, 0.900, 0.861, 0.873, 0.849, 0.856, 0.837,
        0.817, 0.844, 0.797, 0.262, 0.270, 0.257, 0.253, 0.246
    ]

    # Normalize to [0.1, 0.7]
    min_val, max_val = 0.2, 0.9
    new_min, new_max = 0.1, 0.7

    scaled_scales = [
        new_min + ((val - min_val) / (max_val - min_val)) * (new_max - new_min)
        for val in original_scales
    ]

    hour = (time_step // 3600) % 24
    traci.simulation.setScale(scaled_scales[hour])


# Start SUMO
traci.start([sumo_binary, "-c", r"/home/nmit/TMP/sumo/Race_Course 2.0/2025-04-30-10-03-18/osm.sumocfg", "--start"])
time.sleep(2)

# Build edge map for each point
junction_edges_map = {name: [] for _, _, _, name in tracking_points}
for edge_id in traci.edge.getIDList():
    for x, y, radius, name in tracking_points:
        if is_edge_inside_circle(edge_id, x, y, radius):
            junction_edges_map[name].append(edge_id)

# CSV setup
with open("junction_data_race_course.csv", "w", newline="") as csvfile:
    headers = ["Time"]
    for _, _, _, name in tracking_points:
        headers.extend([f"{name}_Count", f"{name}_QueuePct", f"{name}_Speed"])
    writer = csv.writer(csvfile)
    writer.writerow(headers)

    simulation_time = 864000  # 24 hours x 10
    for step in range(simulation_time):
        traci.simulationStep()
        update_traffic_scale(step)

        if step % 600 == 0:
            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            hour = (step // 3600) % 24
            print(f"{current_time} : Sim Time: {step}s : Hour: {hour}")

        row = [step]
        for x, y, radius, name in tracking_points:
            count = 0
            speed_sum = 0.0
            for v_id in traci.vehicle.getIDList():
                vx, vy = traci.vehicle.getPosition(v_id)
                if math.hypot(vx - x, vy - y) <= radius:
                    count += 1
                    speed_sum += traci.vehicle.getSpeed(v_id)
            avg_speed = (speed_sum / count) if count > 0 else 0.0

            edges = junction_edges_map[name]
            total_pct = sum(get_queue_length_percentage(eid) for eid in edges)
            avg_queue_pct = (total_pct / len(edges)) if edges else 0

            row.extend([count, round(avg_queue_pct, 2), round(avg_speed, 2)])

        writer.writerow(row)

traci.close()
print("Simulation completed and data saved.")

