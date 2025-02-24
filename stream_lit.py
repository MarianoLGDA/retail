import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import folium
from shapely.geometry import Point
import joblib

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("data_2021_to_2024.csv")  # Update the path to the dataset

df = load_data()

# Load county shapefile
@st.cache_data
def load_shapefile():
    return gpd.read_file("iowa_counties.shp")  # Update the path to the shapefile

county_map = load_shapefile()

# Title of the Streamlit App
st.title("Iowa Liquor Sales Analysis")

# Step 1: User selects a category (Type of Alcohol)
selected_category = st.selectbox("What type of alcohol are you interested in?", df["category_name"].unique())

# Filter dataframe based on category
filtered_df = df[df["category_name"] == selected_category]

# Step 2: User selects a specific brand (Item Description)
selected_brand = st.selectbox("Select the brand:", filtered_df["item_description"].unique())

# Filter dataframe based on brand
brand_df = filtered_df[filtered_df["item_description"] == selected_brand]

# Step 3: Compute the top 10 counties with highest consumption
top_10_counties = (
    brand_df.groupby("county")["bottles_sold"].sum()
    .reset_index()
    .sort_values(by="bottles_sold", ascending=False)
    .head(10)
)

# Display top 10 counties as a table
st.subheader(f"Top 10 Counties Consuming {selected_brand}")
st.dataframe(top_10_counties)

# Step 4: Map Visualization using GeoPandas
st.subheader("Map of Top 10 Counties")

# Merge with top 10 counties
top_10_map_data = county_map.merge(top_10_counties, left_on="NAME", right_on="county", how="inner")

# Create the map
fig, ax = plt.subplots(figsize=(10, 6))
top_10_map_data.plot(column="bottles_sold", cmap="coolwarm", legend=True, edgecolor="black", ax=ax)
ax.set_title(f"Top 10 Counties for {selected_brand} Sales", fontsize=14)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

# Show the map in Streamlit
st.pyplot(fig)

# Step 5: Interactive Folium Map
st.subheader("Interactive Store Map")

# Define map center
map_center = [df["latitude"].mean(), df["longitude"].mean()]
store_map = folium.Map(location=map_center, zoom_start=7)

# Add store locations as circle markers
for _, row in brand_df.iterrows():
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=4,
        color="blue",
        fill=True,
        fill_color="red",
        fill_opacity=0.6,
        popup=folium.Popup(f"Store: {row['store_name']}<br>County: {row['county']}<br>Sales: ${row['sale_dollars']:.2f}", max_width=300),
    ).add_to(store_map)

# Save and display the interactive map
store_map_path = "store_map.html"
store_map.save(store_map_path)
st.markdown(f"[Click here to view the interactive map](./{store_map_path})")
