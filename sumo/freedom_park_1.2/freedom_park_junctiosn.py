import traci
import math
import time

# Start SUMO
traci.start(["sumo-gui", "-c", "test.sumocfg", "--start"])
time.sleep(2)  # Allow SUMO to initialize

# 🚀 Tracking Locations (x, y, radius, name)
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

# Function to add labels using POIs
def add_label(label_id, position, name, color):
    traci.poi.add(
        poiID=label_id,
        x=position[0],
        y=position[1],
        color=color
    )
    print(f"Added label: {name} at {position}")  # Debugging print

# Draw circles & add labels for all tracking points
for i, (x, y, radius, name) in enumerate(tracking_points):
    draw_detection_zone(i, (x, y), radius, circle_color)
    add_label(f"label_{i}", (x, y), name, label_color)

# Run simulation and count vehicles inside the radius
simulation_time = 500  # Run for 500 steps (adjust as needed)
for step in range(simulation_time):
    traci.simulationStep()

    vehicle_counts = {}
    
    for i, (x, y, radius, name) in enumerate(tracking_points):
        count = 0
        for vehicle in traci.vehicle.getIDList():
            vehicle_x, vehicle_y = traci.vehicle.getPosition(vehicle)

            # Calculate distance from detection point
            distance = math.sqrt((vehicle_x - x)**2 + (vehicle_y - y)**2)
            if distance <= radius:
                count += 1

        vehicle_counts[name] = count

    # Print vehicle count for all locations
    print(f"Step {step}: {vehicle_counts}")

    time.sleep(0.1)  # Slow down visualization slightly

traci.close()
