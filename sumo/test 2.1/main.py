import traci
import math
import csv

# Take user input for GUI mode
gui_mode = 0
sumo_binary = "sumo-gui" if gui_mode == "1" else "sumo"

# Start SUMO
traci.start([sumo_binary, "-c", "test.sumocfg"])

# Define junctions and their IDs
junctions = ['A', 'B', 'C', 'D', 'E']
junction_positions = {j: traci.junction.getPosition(j) for j in junctions}

# Define roads (edges) for velocity tracking
roads = ['AB', 'BC', 'CA', 'CD', 'ED', 'DA']

# Define the distance threshold (in meters) for vehicle counting at junctions
distance_threshold = 20.0

# Function to draw a translucent blue circle around junctions
def draw_circle(junction_id, position, radius, color):
    points = [
        (position[0] + radius * math.cos(angle), position[1] + radius * math.sin(angle))
        for angle in [i * (math.pi / 10) for i in range(21)]
    ]
    traci.polygon.add(junction_id, points, color, fill=True, layer=0)

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

# Only add visualizations if GUI mode is enabled
if gui_mode == "1":
    circle_color = (0, 0, 255, 100)  # Blue with transparency
    for junction in junctions:
        draw_circle(f"circle_{junction}", junction_positions[junction], distance_threshold, circle_color)

# Set simulation scale to 0.5 (constant)
#traci.simulation.setScale(0.5)

# Open a CSV file to store time-series data
with open("traffic_data_dyn.csv", "w", newline="") as csvfile:
    fieldnames = ["Time"] + [f"Vehicle Count at Junction {j}" for j in junctions] + \
                 [f"Avg Speed on {r}" for r in roads]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Simulation loop
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        # Update traffic scale dynamically
        update_traffic_scale(traci.simulation.getTime())

        # Initialize data dictionary
        time_step = traci.simulation.getTime()
        data = {"Time": time_step}

        # Count vehicles at each junction
        for junction in junctions:
            count = 0
            for vehicle in traci.vehicle.getIDList():
                vehicle_position = traci.vehicle.getPosition(vehicle)
                junction_position = junction_positions[junction]

                # Calculate Euclidean distance
                distance = math.sqrt((vehicle_position[0] - junction_position[0])**2 +
                                     (vehicle_position[1] - junction_position[1])**2)

                if distance <= distance_threshold:
                    count += 1

            data[f"Vehicle Count at Junction {junction}"] = count

        # Calculate average speed on each road
        for road in roads:
            vehicle_ids = traci.edge.getLastStepVehicleIDs(road)
            avg_speed = sum(traci.vehicle.getSpeed(v) for v in vehicle_ids) / len(vehicle_ids) if vehicle_ids else 0
            data[f"Avg Speed on {road}"] = avg_speed

        # Write data to CSV
        writer.writerow(data)

traci.close()
