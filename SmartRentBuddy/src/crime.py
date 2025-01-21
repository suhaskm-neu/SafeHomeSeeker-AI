import pandas as pd
import folium
from haversine import haversine, Unit
import os
import geocoder
import requests
from io import StringIO
import os

# Directly set the TEAM_API_KEY for testing
os.environ["TEAM_API_KEY"] = "bb251d2265a7ecc64a5b5d0e422b7c3d85145cb910d580a89d0dfc28da831023"
print("TEAM_API_KEY set directly:", os.environ.get("TEAM_API_KEY"))




from aixplain.factories import PipelineFactory
def create_report(input_data):
    pipeline = PipelineFactory.get("66fdba8ae3d95ac47f8eebcf")
    result = pipeline.run(input_data)
    url = result['data'][0]['segments'][0]['response']
    response = requests.get(url)
    if response.status_code == 200:
        print(response.text)
        return response.text
    else:
        return "we have no information at this time"

# Load the crime data
g = geocoder.ip('me')
if g.ok:
    latitude = g.latlng[0]  
    longitude = g.latlng[1]

print(longitude,latitude)

try:
    crime_data = pd.read_csv("/Users/terrelldavis/Desktop/Personal Projects/SmartRentBuddy/dc-crimes-search-results.csv")
    print("CSV file loaded successfully.")
except Exception as e:
    print(f"Error loading CSV file: {e}")


def split_coordinates(coord):
    lat_str, lon_str = coord.split(",")
    return float(lat_str), float(lon_str)

crime_data[['latitude', 'longitude']] = crime_data['location'].apply(split_coordinates).apply(pd.Series)

# Set the map center and radius
map_center = [38.8951, -77.0364]
mile_radius = 1609.34

# Create the initial map
my_map = folium.Map(location=map_center, max_zoom=12)

# Create the circle
circle = folium.Circle(
    location=map_center,
    radius=mile_radius * 5,
    color='blue',
    fill=True,
    fill_color='blue',
    fill_opacity=0.1,
    popup='5 Mile Radius'
).add_to(my_map)

# Function to update the circle and add markers
def update_circle(curx, cury ,miles,useloc):
    if useloc and g.ok and g.latlng:
        latitude, longitude = g.latlng  
    else :
        latitude, longitude = curx,cury 
    
    my_map = folium.Map(location=[latitude, longitude], zoom_start=12)  
    circle = folium.Circle(
    location=[latitude, longitude],
    radius=mile_radius * miles,
    color='blue',
    fill=True,
    fill_color='blue',
    fill_opacity=0.1,
    popup='5 Mile Radius'
    ).add_to(my_map)
    r = 0
    folium.Marker(location=[latitude, longitude], popup="me").add_to(my_map)
    lst = []
    
    for index, row in crime_data.iterrows():
        x = row['latitude']
        y = row['longitude']
        crime_committed = row["OFFENSE"]
        point = (x, y)
        center = (curx, cury)
        distance = haversine(center, point, unit=Unit.METERS) #determines the great-circle distance between two points on a sphere
        if distance < mile_radius * miles:  # Check against the radius
             if  r < 25: # at 25 because any more reach input limit with pipeline
                lst.append(row)
                folium.Marker(location=[x, y], popup=f"{crime_committed}").add_to(my_map)
                r += 1  
                print(f"Added marker at {x}, {y}. Total markers: {r}")  # Print marker info
    
    filtered_crime_data = pd.DataFrame(lst)
    input_string = StringIO()
    filtered_crime_data.to_csv(input_string, index=False)

    csv_output = input_string.getvalue()

    # Save the updated map
    my_map.save("SmartRentBuddy/map.html")

    return create_report(csv_output)
    
print(update_circle(map_center[0],map_center[1],1,False))


