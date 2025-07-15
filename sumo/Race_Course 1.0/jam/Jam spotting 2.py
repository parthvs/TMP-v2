import traci
import math

# 1) Junction definitions
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

# 2) Jam thresholds
thresholds = {
    "FP_A": 40, "FP_B": 3, "FP_C": 5, "FP_D": 15,
    "KR_Circle": 20, "KG_Road": 15,
    "District_Office": 10, "Anand_Rao_Jnc": 6,
    "Race_Course_Jnc": 10, "Palace_Road_Jnc": 20
}

# 3) Launch SUMO GUI and set scale
cfg = r"C:\Users\USER\projects\TMPv2\sumo\Race_Course 1.0\2025-04-22-17-42-06\osm.sumocfg"
traci.start([
    "sumo",
    "-c", cfg,
    "--start",
    "--record-replay", "replay.xml",           # Full sim replay
    "--fcd-output", "fcd_output.xml"           # Vehicle trace data
])
traci.simulation.setScale(5)

# 4) Draw detection circles
circle_color = (0, 0, 255, 100)
for xc, yc, r, name in tracking_points:
    pts = [
        (xc + r * math.cos(a), yc + r * math.sin(a))
        for a in [i * (math.pi / 10) for i in range(21)]
    ]
    traci.polygon.add(f"detect_{name}", pts, circle_color, fill=True, layer=1)
    traci.polygon.setLineWidth(f"detect_{name}", 2.0)

# 5) Map edges to junctions
def is_edge_inside_circle(eid, x0, y0, r):
    try:
        fj, tj = traci.edge.getFromJunction(eid), traci.edge.getToJunction(eid)
        x1, y1 = traci.junction.getPosition(fj)
        x2, y2 = traci.junction.getPosition(tj)
        return (math.hypot(x1 - x0, y1 - y0) <= r or math.hypot(x2 - x0, y2 - y0) <= r)
    except:
        return False

junction_edges = {name: [] for *_, name in tracking_points}
for eid in traci.edge.getIDList():
    for x, y, r, name in tracking_points:
        if is_edge_inside_circle(eid, x, y, r):
            junction_edges[name].append(eid)

# 6) Queue percentage helper
def queue_pct(edge_id):
    try:
        n = traci.edge.getLastStepVehicleNumber(edge_id)
        length = traci.lane.getLength(edge_id + "_0")
        return (n / length) * 100 if length > 0 else 0
    except:
        return 0

# 7) Simulation loop (simplified output)
while traci.simulation.getMinExpectedNumber() > 0:
    traci.simulationStep()

    for x, y, r, name in tracking_points:
        edges = junction_edges[name]
        avg_q = (sum(queue_pct(e) for e in edges) / len(edges)) if edges else 0.0

        cnt = 0
        spd_sum = 0.0
        for vid in traci.vehicle.getIDList():
            vx, vy = traci.vehicle.getPosition(vid)
            if math.hypot(vx - x, vy - y) <= r:
                cnt += 1
                spd_sum += traci.vehicle.getSpeed(vid)
        avg_spd = (spd_sum / cnt) if cnt > 0 else 0.0

        threshold_val = thresholds[name]
        print(f"{name}: {avg_spd:.2f}, {avg_q:.2f}, {threshold_val}")

        if avg_spd < 0.1 and avg_q > threshold_val:
            print(f"Jam at {name}")
            traci.polygon.setColor(f"detect_{name}", (255, 0, 0, 100))
        else:
            traci.polygon.setColor(f"detect_{name}", (0, 0, 255, 100))

# 8) End simulation
traci.close()
