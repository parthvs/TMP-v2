import xml.etree.ElementTree as ET
import pandas as pd

xml_file = "detector_output.xml"
csv_file = "detector_output.csv"

# Load and parse XML
try:
    tree = ET.parse(xml_file)
    root = tree.getroot()
    print("XML file loaded successfully!")
except Exception as e:
    print(f"Error loading XML: {e}")
    exit()

# Extract data
data = []
for interval in root.findall(".//interval"):
    print(f"Processing: {interval.attrib}")  # Debug print
    data.append([
        interval.get("begin"),
        interval.get("end"),
        interval.get("id"),
        interval.get("nVehEntered"),
        interval.get("flow"),
        interval.get("occupancy"),
        interval.get("speed"),
        interval.get("harmonicMeanSpeed"),
    ])

# Convert to DataFrame
df = pd.DataFrame(data, columns=[
    "StartTime", "EndTime", "DetectorID", "VehicleCount",
    "Flow", "Occupancy", "Speed", "HarmonicMeanSpeed"
])

if df.empty:
    print("No data extracted from XML.")
else:
    df.to_csv(csv_file, index=False)
    print(f"CSV file saved as {csv_file}")
