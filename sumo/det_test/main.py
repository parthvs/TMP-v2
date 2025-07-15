import traci
import math

# Start SUMO with GUI
traci.start(['sumo-gui', '-c', 'test.sumocfg'])

# Define junctions and their IDs
junctions = ['A', 'B', 'C']
junction_positions = {j: traci.junction.getPosition(j) for j in junctions}

# Define the distance threshold (in meters)
distance_threshold = 20.0

# Function to draw a translucent blue circle
def draw_circle(junction_id, position, radius, color):
    points = [
        (position[0] + radius * math.cos(angle), position[1] + radius * math.sin(angle))
        for angle in [i * (math.pi / 10) for i in range(21)]
    ]
    traci.polygon.add(junction_id, points, color, fill=True, layer=0)

# Add the translucent circles once at the beginning
circle_color = (0, 0, 255, 100)  # Blue with transparency
for junction in junctions:
    draw_circle(f"circle_{junction}", junction_positions[junction], distance_threshold, circle_color)

# Simulation loop
while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()
    
    # Initialize vehicle counts for each junction
    vehicle_counts = {j: 0 for j in junctions}
    
    # Get all active vehicles
    vehicles = traci.vehicle.getIDList()
    
    for vehicle in vehicles:
        vehicle_position = traci.vehicle.getPosition(vehicle)
        
        for junction, junction_position in junction_positions.items():
            # Calculate Euclidean distance
            distance = math.sqrt((vehicle_position[0] - junction_position[0])**2 +
                                 (vehicle_position[1] - junction_position[1])**2)
            
            if distance <= distance_threshold:
                vehicle_counts[junction] += 1
    
    # Output the vehicle counts for each junction
    for junction, count in vehicle_counts.items():
        print(f"Time {traci.simulation.getTime()}s: Junction {junction} has {count} vehicles within {distance_threshold} meters.")

traci.close()
