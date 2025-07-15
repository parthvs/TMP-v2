import traci
import math
import csv
import time

# Take user input for GUI mode
gui_mode = input("1 for gui and 0 for non gui")  # Change to "0" for non-GUI mode
sumo_binary = "sumo-gui" if gui_mode == "1" else "sumo"

# Start SUMO
traci.start([sumo_binary, "-c", "test.sumocfg", "--start"])
time.sleep(2)  # Allow SUMO to initialize

# 🚀 Tracking Locations (x, y, radius, name) - Column names match exactly!
tracking_points = [
    (590.85, 1079.43, 50.0, "Junction 1"),
    (1566.25, 1260.03, 50.0, "Big Roundabout"),
    (1043.77, 1175.63, 50.0, "Junction 2"),
    (771.77, 1354.39, 50.0, "Junction 3"),
    (971.33, 1673.16, 50.0, "Junction 4"),
    (1245.12, 1491.37, 50.0, "Junction 5")
]

# Define colors
circle_color = (0, 0, 255, 100)  # Blue circles
label_color = (255, 255, 255, 255)  # White labels

# Function to draw detection zones
def draw_detection_zone(point_id, position, radius, color):
    points = [
        (position[0] + radius * math.cos(angle), position[1] + radius * math.sin(angle))
        for angle in [i * (math.pi / 10) for i in range(21)]
    ]
    traci.polygon.add(f"detection_{point_id}", points, color, fill=True, layer=1)

# Function to add large labels using POIs
def add_label(label_id, position, name, color):
    traci.poi.add(
        poiID=label_id,
        x=position[0],
        y=position[1],
        color=color
    )
    print(f"Added label: {name} at {position}")  # Debugging print

# Only draw visuals if GUI mode is enabled
if gui_mode == "1":
    for i, (x, y, radius, name) in enumerate(tracking_points):
        draw_detection_zone(i, (x, y), radius, circle_color)
        add_label(f"label_{i}", (x, y), name, label_color)

# Function to set traffic scale based on time of day
def update_traffic_scale(time_step):
    hour = (time_step // 3600) % 24  # Convert simulation time (seconds) to hours

    if 0 <= hour < 4:
        traci.simulation.setScale(0.1)
    elif 4 <= hour < 7:
        traci.simulation.setScale(0.2)
    elif 7 <= hour < 12:
        traci.simulation.setScale(0.4)
    elif 12 <= hour < 15:
        traci.simulation.setScale(0.7)
    elif 15 <= hour < 19:
        traci.simulation.setScale(0.2)
    elif 19 <= hour < 22:
        traci.simulation.setScale(0.4)
    elif 22 <= hour < 24:
        traci.simulation.setScale(0.2)

# Open CSV file to store time-series data
with open("null_junction_data.csv", "w", newline="") as csvfile:
    # **Column names match exactly the provided junction names**
    fieldnames = ["Time"] + [name for _, _, _, name in tracking_points]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Simulation loop
    simulation_time = 86400
    for step in range(simulation_time):
        traci.simulationStep()

        # Update traffic scale dynamically
        update_traffic_scale(traci.simulation.getTime())

        vehicle_counts = {"Time": step}

        for x, y, radius, name in tracking_points:
            count = 0
            for vehicle in traci.vehicle.getIDList():
                vehicle_x, vehicle_y = traci.vehicle.getPosition(vehicle)

                # Calculate distance from detection point
                distance = math.sqrt((vehicle_x - x) ** 2 + (vehicle_y - y) ** 2)
                if distance <= radius:
                    count += 1

            vehicle_counts[name] = count  # Store vehicle count under correct name

        # Write data to CSV
        writer.writerow(vehicle_counts)

        # Print vehicle count for all locations
        #print(f"Step {step}: {vehicle_counts}")

        time.sleep(0.1)  # Slow down visualization slightly

traci.close()
