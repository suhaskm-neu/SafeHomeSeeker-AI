# Import necessary modules
import os
os.environ["TEAM_API_KEY"] = ""
import json
import folium
import pandas as pd
from haversine import haversine, Unit
from io import StringIO
from aixplain.factories import ModelFactory
import streamlit as st
from langchain_openai.embeddings import OpenAIEmbeddings
import pinecone
import geocoder
from aixplain.factories import ModelFactory, PipelineFactory
from io import StringIO
from pinecone.grpc import PineconeGRPC as Pinecone
import requests

# Set up API keys
os.environ["OPENAI_API_KEY"] = ""
os.environ["PINECONE_API_KEY"] = ""
RAPIDAPI_KEY = ""  
RAPIDAPI_HOST = "google-map-places.p.rapidapi.com"

# Initialize AiXplain and Pinecone models
model = ModelFactory.get("6414bd3cd09663e9225130e8")
embeddings = OpenAIEmbeddings()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("housedb-v4")

# Load crime data
crime_data = pd.read_csv("dc-crime-search-results.csv")

# Helper function to split and convert coordinates
def split_coordinates(coord):
    lat_str, lon_str = coord.split(",")
    return float(lat_str), float(lon_str)

crime_data[['latitude', 'longitude']] = crime_data['location'].apply(split_coordinates).apply(pd.Series)

# Function to generate the map and return as HTML string
def create_house_map(latitude, longitude, house_id, miles_radius=2):
    my_map = folium.Map(location=[latitude, longitude], zoom_start=12)
    folium.Circle(
        location=[latitude, longitude],
        radius=1609.34 * miles_radius,
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.1,
        popup=f'{miles_radius} Mile Radius'
    ).add_to(my_map)
    folium.Marker(location=[latitude, longitude], popup=f"House ID: {house_id}").add_to(my_map)
    markers_added = 0
    for _, row in crime_data.iterrows():
        crime_lat, crime_lon = row['latitude'], row['longitude']
        if haversine((latitude, longitude), (crime_lat, crime_lon), unit=Unit.METERS) <= 1609.34 * miles_radius and markers_added < 25:
            folium.Marker(location=[crime_lat, crime_lon], popup=row["OFFENSE"]).add_to(my_map)
            markers_added += 1
    return my_map._repr_html_()

# Function to beautify descriptions using AiXplain model
def beautify_descriptions(houses):
    if not houses:
        return []
    
    descriptions = "\n".join([f"{i+1}. {house['description']}" for i, house in enumerate(houses)])
    model_output = model.run({
        "text": f"""
            Paraphrase the following descriptions of houses:\n{descriptions}.
            Your job is to just describe these houses. You dont need to worry about making it
            sound very persuasuve. Just give all the details. Dont include the latitudes and longitudes and 
            FOR_LEASE/FOR_BUY info in the description. Start the description by its ZPID like this:
            ZPID: 12345678: Then describe the house. And if the desctiption is empty, just output "Currently no Options for these filters"
            """,
        "max_tokens": 1000,
        "temperature": 0.5,
    })
    
    beautified_descriptions = model_output.get('data', '').split('\n\n')
    for i, house in enumerate(houses):
        if i < len(beautified_descriptions):
            house['description'] = beautified_descriptions[i].strip()
    return houses

# Streamlit UI for input and displaying maps
st.title("Smart House Finder")
zip_code_input = st.text_input("Enter ZIP code")
rent_or_buy = st.selectbox("Rent/Buy", ["Rent", "Buy"])
bedrooms = st.selectbox("Bedrooms", [1, 2, 3, 4, 5])
bathrooms = st.selectbox("Bathrooms", [1, 2, 3, 4, 5])

# Dynamically adjust budget range based on Rent or Buy selection
if rent_or_buy == "Rent":
    budget = st.slider("Budget", 0, 10000)
else:
    budget = st.slider("Budget", 0, 10000000)

# Additional UI elements and amenities selection
st.write("Select the public amenities you're interested in:")
amenities = []
if st.checkbox("School"):
    amenities.append("School")
if st.checkbox("Park"):
    amenities.append("Park")
if st.checkbox("Bank"):
    amenities.append("Bank")
if st.checkbox("Grocery stores"):
    amenities.append("Grocery stores")
if st.checkbox("Gym"):
    amenities.append("Gym")

# ... [rest of the code]

if st.button("Submit"):
    query = f"I want to {rent_or_buy.lower()} a property in ZIP code {zip_code_input} with {bedrooms} bedrooms and {bathrooms} bathrooms. My budget is ${budget}."
    query_embedding = embeddings.embed_query(query)
    response = index.query(
        vector=query_embedding,
        filter={
            "price": {"$lt": budget},
            "zipcode": {"$eq": int(zip_code_input)},
            "bedrooms": {"$eq": bedrooms},
            "bathrooms": {"$eq": bathrooms},
        },
        include_metadata=True,
        top_k=5,
    )

    def extract_house_data(response_json):
        houses = []
        for match in response_json.get('matches', []):
            metadata = match.get('metadata', {})
            zpid = metadata.get('zpid')
            text = metadata.get('text')
            latitude = float(text.split('Latitude: ')[1].split(', ')[0])
            longitude = float(text.split('Longitude: ')[1].split('.')[0])
            if zpid and text:
                houses.append({
                    "zpid": zpid,
                    "description": text,
                    "latitude": latitude,
                    "longitude": longitude
                })
        return houses

    # Extract house data from the response
    houses = extract_house_data(response.to_dict())
    
    # Check if any houses were found
    if not houses:
        st.write("Currently, no options are available for these filters. Please try adjusting your criteria.")
    else:
        beautified_houses = beautify_descriptions(houses)
        
        # Display each house with its beautified description and map
        for house in beautified_houses:
            st.markdown(f"### House ZPID: {house['zpid']}")
            st.markdown(f"**Description:** {house['description']}")
            map_html = create_house_map(house["latitude"], house["longitude"], house["zpid"])
            st.components.v1.html(map_html, width=700, height=500)
            st.markdown("---")
