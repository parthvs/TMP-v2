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

# Extract junction names for column headers
junction_names = [name for (_, _, _, name) in tracking_points]

# Define colors (optional for visualization)
circle_color = (0, 0, 255, 100)  # Blue circles
label_color = (255, 255, 255, 255)  # White labels

# Function to draw detection zones (optional for visualization)
def draw_detection_zone(point_id, position, radius, color):
    points = [
        (position[0] + radius * math.cos(angle), position[1] + radius * math.sin(angle))
        for angle in [i * (math.pi / 10) for i in range(21)]
    ]
    traci.polygon.add(f"detection_{point_id}", points, color, fill=True, layer=1)

# Function to add labels using POIs (optional for visualization)
def add_label(label_id, position, name, color):
    traci.poi.add(
        poiID=label_id,
        x=position[0],
        y=position[1],
        color=color
    )
    print(f"Added label: {name} at {position}")

# Draw circles & add labels for all tracking points (optional for visualization)
for i, (x, y, radius, name) in enumerate(tracking_points):
    draw_detection_zone(i, (x, y), radius, circle_color)
    add_label(f"label_{i}", (x, y), name, label_color)

# Run simulation and monitor vehicle counts and speeds
simulation_time = 5000  # Number of steps

# Print table header
print("\nStep", " | ".join(f"{name:^15}" for name in junction_names))
print("-" * (6 + 18 * len(junction_names)))

# Simulation loop
for step in range(simulation_time):
    traci.simulationStep()

    # Dictionary to store vehicle stats (count and avg speed) per junction
    vehicle_stats = {}

    for i, (x, y, radius, name) in enumerate(tracking_points):
        count = 0
        speed_sum = 0.0

        for vehicle in traci.vehicle.getIDList():
            vehicle_x, vehicle_y = traci.vehicle.getPosition(vehicle)
            distance = math.sqrt((vehicle_x - x) ** 2 + (vehicle_y - y) ** 2)

            if distance <= radius:
                count += 1
                speed_sum += traci.vehicle.getSpeed(vehicle)

        # Calculate average speed, handle division by zero
        avg_speed = (speed_sum / count) if count > 0 else 0.0
        vehicle_stats[name] = {
            "count": count,
            "avg_speed": round(avg_speed, 2)
        }

    # Print the average speeds for this step
    speed_row = [f"{vehicle_stats[name]['avg_speed']:^15.2f}" for name in junction_names]
    print(f"{step:<4} " + " | ".join(speed_row))

    time.sleep(0.1)  # Optional: to slow down visualization slightly

# Close the simulation
traci.close()
