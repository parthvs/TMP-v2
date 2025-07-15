import traci
import math
import time
import matplotlib.pyplot as plt
import numpy as np

# Define the tracking points (junctions with circles)
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
    (1836.39, 1677.60, 50.0, "Palace_Road_Jnc")
]

path = r"C:\Users\USER\projects\TMPv2\sumo\Race_Course 1.0\2025-04-22-17-42-06\osm.sumocfg"

# Start SUMO
traci.start(["sumo-gui", "-c", path, "--start"])
time.sleep(2)

# Edge mapping
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

junction_edges_map = {name: [] for _, _, _, name in tracking_points}
for edge_id in traci.edge.getIDList():
    for x, y, radius, name in tracking_points:
        if is_edge_inside_circle(edge_id, x, y, radius):
            junction_edges_map[name].append(edge_id)

def get_queue_length_percentage(edge_id):
    try:
        num_vehicles = traci.edge.getLastStepVehicleNumber(edge_id)
        total_length = sum(
            traci.lane.getLength(f"{edge_id}_{i}")
            for i in range(traci.edge.getLaneNumber(edge_id))
        )
        return (num_vehicles / total_length) * 100 if total_length > 0 else 0
    except:
        return 0

# Set up dynamic plotting
plt.ion()
fig, axes = plt.subplots(len(tracking_points), 2, figsize=(10, 2 * len(tracking_points)))

# Store data for plotting
queue_data = {name: [] for _, _, _, name in tracking_points}
speed_data = {name: [] for _, _, _, name in tracking_points}

# Run simulation
for t in range(4000):
    traci.simulationStep()
    
    for i, (x, y, radius, name) in enumerate(tracking_points):
        # Queue Length
        edges = junction_edges_map[name]
        total_pct = sum(get_queue_length_percentage(eid) for eid in edges)
        avg_queue = total_pct / len(edges) if edges else 0

        # Speed
        count = 0
        speed_sum = 0.0
        for vehicle_id in traci.vehicle.getIDList():
            vx, vy = traci.vehicle.getPosition(vehicle_id)
            distance = math.hypot(vx - x, vy - y)
            if distance <= radius:
                count += 1
                speed_sum += traci.vehicle.getSpeed(vehicle_id)
        avg_speed = (speed_sum / count) if count > 0 else 0.0

        # Store data for plotting
        queue_data[name].append(avg_queue)
        speed_data[name].append(avg_speed)

        # Update the plots dynamically
        axes[i, 0].cla()  # Clear axis for queue plot
        axes[i, 1].cla()  # Clear axis for speed plot

        axes[i, 0].plot(queue_data[name], label=f"{name} Queue", color='b')
        axes[i, 1].plot(speed_data[name], label=f"{name} Speed", color='r')

        axes[i, 0].set_title(f"{name} Queue")
        axes[i, 1].set_title(f"{name} Speed")

        axes[i, 0].set_xlabel("Time")
        axes[i, 0].set_ylabel("Queue Length (%)")

        axes[i, 1].set_xlabel("Time")
        axes[i, 1].set_ylabel("Speed (m/s)")

    plt.pause(0.05)  # Pause for a short time to update the plot

# Close SUMO
traci.close()
