# Smart House Finder

- **Published Blog Link** [Blog](https://beta.openai.com/signup/](https://aixplain.com/blog/community-story-dc-safehomeseeker-ai-property-search/).

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [UI Functionality](#ui-functionality)
- [Data Sources](#data-sources)
- [Implementation Details](#implementation-details)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Project Overview

**Smart House Finder** is a real estate search tool that allows users to locate rental or purchase properties within a specified ZIP code and filter options based on budget, number of bedrooms, bathrooms, and additional public amenities. The application is powered by AI for enhancing property descriptions and includes real-time map generation with crime data overlays to help users make informed decisions.

This application is built with Python and Streamlit for a responsive web UI, Pinecone for vector search, and OpenAI for embeddings, among other powerful technologies.

---

## Features

- **Dynamic Search Filters**: Users can specify various filters including rent/buy options, budget, bedrooms, bathrooms, and ZIP code.
- **Real-Time Crime Data Overlay**: Property maps include markers for recent crimes in the area, providing an added layer of safety information.
- **AI-Powered Descriptions**: Automatically beautify property descriptions using OpenAI language models for enhanced readability.
- **Interactive Map Visualizations**: Properties are displayed on an interactive map with radius markers and crime data overlays.
- **Public Amenities Selection**: Users can choose nearby public amenities such as parks, gyms, schools, and more to refine their property search.
- **User Feedback for No Results**: Informs users when no properties match their search criteria, encouraging adjustments to filters.

---

## Tech Stack

### Frontend
- **Streamlit**: Used for the user interface, handling all user interactions and visualizations.

### Backend
- **Python**: Core programming language for the application.
- **Pinecone**: Used for vector search of property descriptions and data storage.
- **OpenAI Embeddings**: Generates embeddings for property search and data enrichment.
- **RapidAPI**: Integrated for Google Places API to fetch public amenities data.
- **Folium**: Creates interactive maps with crime data overlays.
- **Pandas**: For data manipulation and management.
- **Geocoder**: Fetches the user’s location details for better relevance.

---

## Setup and Installation

### Prerequisites
Ensure you have Python 3.8+ installed. You will also need API keys for:
- **OpenAI**: Obtain an API key from [OpenAI](https://beta.openai.com/signup/).
- **Pinecone**: Obtain an API key from [Pinecone](https://www.pinecone.io/).
- **RapidAPI**: Obtain an API key from [RapidAPI](https://rapidapi.com/).

### Installation Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/smart-house-finder.git
   cd smart-house-finder
   ```

2. **Install Dependencies**: Create a virtual environment and install required packages:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Environment Variables**: Set up environment variables for API keys:
   ```bash
   export OPENAI_API_KEY='your-openai-api-key'
   export PINECONE_API_KEY='your-pinecone-api-key'
   export RAPIDAPI_KEY='your-rapidapi-key'
   export RAPIDAPI_HOST='google-map-places.p.rapidapi.com'
   ```

4. **Download the Crime Data**: Place the `dc-crime-search-results.csv` file in the root directory of the project.

---

## Usage

To start the application, run the following command:
```bash
streamlit run app.py
```

Navigate to [http://localhost:8501](http://localhost:8501) in your web browser to access the application.

### Search Parameters
- **ZIP Code**: Enter the ZIP code to search within.
- **Rent/Buy**: Specify whether you are looking to rent or buy a property.
- **Budget**: Set the budget range based on rent or buy preference.
- **Bedrooms/Bathrooms**: Select the number of bedrooms and bathrooms.
- **Public Amenities**: Choose amenities such as gyms, parks, schools, etc.
- Click the **Submit** button to view results.

---

## UI Functionality

- **Property Filters**: The budget slider dynamically adjusts based on Rent (up to $10k) or Buy (up to $10M).
- **Results Display**: If properties are found, they display with a beautified description and an interactive map. If not, a message appears.
- **Map Visualization**: Maps show the property’s location and crime data markers within a specified radius.
- **Public Amenities Data**: Display nearby amenities based on user selection using the Google Places API.

---

## Data Sources

- **Pinecone Database**: Holds property embeddings for efficient vector search.
- **dc-crime-search-results.csv**: CSV file containing crime data for property overlay on maps.
- **Google Places API**: Provides data on nearby public amenities.

---

## Implementation Details

### Crime Data Processing
Crime data is read from a CSV file (`dc-crime-search-results.csv`) using Pandas. The data includes various fields such as crime type, date, and location coordinates (latitude and longitude). The processing steps are as follows:
1. **Data Loading**: The CSV file is loaded into a Pandas DataFrame.
   ```python
   import pandas as pd
   crime_data = pd.read_csv('dc-crime-search-results.csv')
   ```
2. **Data Cleaning**: Any missing or inconsistent data is handled. For example, rows with missing coordinates are dropped.
   ```python
   crime_data.dropna(subset=['latitude', 'longitude'], inplace=True)
   ```
3. **Data Transformation**: The latitude and longitude are extracted and converted into a format suitable for map overlay.
   ```python
   crime_locations = crime_data[['latitude', 'longitude']].values.tolist()
   ```

### AI-Enhanced Descriptions
Property descriptions are enhanced using OpenAI’s language models to make them more engaging and readable. The steps include:
1. **Data Preparation**: Property details are compiled into a structured format.
   ```python
   property_details = {
       'address': '123 Main St',
       'price': '$500,000',
       'bedrooms': 3,
       'bathrooms': 2,
       'description': 'A cozy 3-bedroom house...'
   }
   ```
2. **API Request**: The details are sent to the OpenAI API to generate an enhanced description.
   ```python
   import openai
   openai.api_key = 'your-openai-api-key'
   response = openai.Completion.create(
       engine="text-davinci-003",
       prompt=f"Beautify this property description: {property_details['description']}",
       max_tokens=150
   )
   enhanced_description = response.choices[0].text.strip()
   ```
3. **Integration**: The enhanced description is integrated back into the property details.
   ```python
   property_details['description'] = enhanced_description
   ```

### Interactive Map
Folium is used to generate interactive maps that display property locations and nearby crime incidents. The implementation involves:
1. **Map Initialization**: A Folium map is initialized centered around the property location.
   ```python
   import folium
   property_location = [38.89511, -77.03637]  # Example coordinates
   map = folium.Map(location=property_location, zoom_start=13)
   ```
2. **Adding Property Marker**: A marker is added to the map for the property location.
   ```python
   folium.Marker(location=property_location, popup='Property Location').add_to(map)
   ```
3. **Adding Crime Markers**: Crime incident markers are added to the map.
   ```python
   for location in crime_locations:
       folium.Marker(location=location, icon=folium.Icon(color='red')).add_to(map)
   ```
4. **Dynamic Updates**: The map updates dynamically based on user interactions and selected properties.

### Public Amenities
The Google Places API via RapidAPI is used to fetch and display nearby public amenities. The steps include:
1. **API Request**: An API request is made to fetch amenities based on the property location and user preferences.
   ```python
   import requests
   url = "https://google-map-places.p.rapidapi.com/place/nearbysearch/json"
   querystring = {"location":"38.89511,-77.03637","radius":"1500","type":"gym"}
   headers = {
       'x-rapidapi-key': "your-rapidapi-key",
       'x-rapidapi-host': "google-map-places.p.rapidapi.com"
   }
   response = requests.request("GET", url, headers=headers, params=querystring)
   amenities = response.json().get('results', [])
   ```
2. **Data Parsing**: The response is parsed to extract relevant information about each amenity.
   ```python
   amenities_list = []
   for amenity in amenities:
       amenities_list.append({
           'name': amenity['name'],
           'address': amenity['vicinity'],
           'location': [amenity['geometry']['location']['lat'], amenity['geometry']['location']['lng']]
       })
   ```
3. **Map Integration**: The amenities are displayed on the interactive map.
   ```python
   for amenity in amenities_list:
       folium.Marker(location=amenity['location'], popup=amenity['name']).add_to(map)
   ```

The output of these implementations is a highly interactive and informative real estate search tool that provides users with enhanced property descriptions, real-time crime data overlays, and nearby public amenities, all visualized on an interactive map.

---

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**.
2. **Create a feature branch**.
3. **Commit your changes and push them**.
4. **Submit a pull request**.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for more information.

---

## Acknowledgments

- **OpenAI** for their powerful language models.
- **Pinecone** for enabling vector search capabilities.
- **RapidAPI** and **Google Places API** for public amenities data.
- **Folium** and **Pandas** for data processing and visualization.

Thank you for exploring Smart House Finder. We hope this tool assists you in finding the perfect home!

