import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import re
import os

# -------------------------------------------
# Azure ML Endpoint Configuration
# -------------------------------------------
API_URL = 'http://060fd6ad-695f-4ef8-a9b2-24f8243c2f3d.eastus2.azurecontainer.io/score'
API_KEY = 'aMv3SZnrX4pkyuwhigofZ3mRG2dvhS2B'  # Replace with your actual API key if needed

# File to store form submissions
SUBMISSIONS_FILE = "submissions.csv"

# -------------------------------------------
# App Title & Description
# -------------------------------------------
st.title("Laptop Specification Form & Price Predictor")
st.markdown("""
This app predicts the price of a laptop based on your input specifications.
It also saves your submission and displays sidebar graphs:
- **Average Price by Brand**
- **Price vs. RAM**
- **5 Most Popular CPUs from Submissions**

The machine learning models are deployed on Azure Machine Learning.
""")


# -------------------------------------------
# Sidebar: Other Graphs (Average Price by Brand, Price vs. RAM)
# -------------------------------------------
@st.cache_data
def load_data():
    """
    Loads and cleans the laptop dataset.
    Assumes the CSV file uses the following column names:
    Brand, Processor, RAM_GB, Storage, GPU, Screen_Size_inch, Resolution, Battery_Life_hours, Weight_kg, Operating_System, Price_$
    """
    try:
        data = pd.read_csv("laptop.csv")
    except Exception as e:
        st.error(f"Error loading CSV file: {e}")
        return pd.DataFrame()

    # Remove extra whitespace from column names.
    data.columns = [col.strip() for col in data.columns]
    #st.write("Columns in dataset:", data.columns.tolist())

    # Process the 'RAM_GB' column: extract numeric portion if stored as a string.
    if "RAM_GB" in data.columns:
        try:
            if data["RAM_GB"].dtype == object:
                data["RAM_GB"] = data["RAM_GB"].str.extract(r"(\d+)", expand=False)
            data["RAM_GB"] = pd.to_numeric(data["RAM_GB"], errors="coerce")
        except Exception as e:
            st.error(f"Error processing 'RAM_GB': {e}")
    else:
        st.error("Column 'RAM_GB' not found in the dataset.")

    # Process the 'Storage' column: convert values like "1TB SSD" to numeric (in GB).
    def convert_storage(s):
        s = str(s)
        match = re.search(r"(\d+(\.\d+)?)", s)
        if match:
            value = float(match.group(1))
            if "TB" in s.upper():
                value *= 1024  # Convert TB to GB
            return value
        return None

    if "Storage" in data.columns:
        try:
            data["Storage"] = data["Storage"].apply(convert_storage)
        except Exception as e:
            st.error(f"Error processing 'Storage': {e}")
    else:
        st.error("Column 'Storage' not found in the dataset.")

    # Process the 'Price_$' column: remove '$' symbols/commas and convert to numeric.
    if "Price_$" in data.columns:
        try:
            data["Price_$"] = data["Price_$"].astype(str).replace({r"\$": "", ",": ""}, regex=True)
            data["Price_$"] = pd.to_numeric(data["Price_$"], errors="coerce")
        except Exception as e:
            st.error(f"Error processing 'Price_$': {e}")
    else:
        st.error("Column 'Price_$' not found in the dataset.")

    return data


# Load the full dataset (for sidebar graphs)
df = load_data()

# Sidebar Graph: Average Price by Brand (each brand in a different color)
if "Brand" in df.columns and "Price_$" in df.columns:
    price_by_brand = df.groupby("Brand")["Price_$"].mean().reset_index()
    fig_brand = px.bar(
        price_by_brand,
        x="Brand",
        y="Price_$",
        color="Brand",  # Each brand gets its own distinct color.
        title="Average Price by Brand",
        labels={"Price_$": "Average Price ($)"}
    )
    st.sidebar.plotly_chart(fig_brand, use_container_width=True)
else:
    st.sidebar.error("Required columns for brand analysis not found.")

# Sidebar Graph: Price vs. RAM.
if "RAM_GB" in df.columns and "Price_$" in df.columns:
    fig_ram = px.scatter(
        df,
        x="RAM_GB",
        y="Price_$",
        color="Brand",
        title="Price vs. RAM",
        labels={"RAM_GB": "RAM (GB)", "Price_$": "Price ($)"}
    )
    st.sidebar.plotly_chart(fig_ram, use_container_width=True)
else:
    st.sidebar.error("Required columns for RAM analysis not found.")

# -------------------------------------------
# Sidebar: Container for CPU Popularity Graph (5 Most Popular CPUs)
# -------------------------------------------
cpu_graph_container = st.sidebar.empty()  # Reserve a slot for the CPU graph


def update_cpu_graph(container):
    """Updates the CPU popularity graph (top 5 CPUs from submissions) in the given container."""
    if os.path.exists(SUBMISSIONS_FILE):
        submissions_df = pd.read_csv(SUBMISSIONS_FILE)
    else:
        submissions_df = pd.DataFrame()

    if not submissions_df.empty and "Processor" in submissions_df.columns:
        cpu_counts = submissions_df["Processor"].value_counts().nlargest(5).reset_index()
        cpu_counts.columns = ["Processor", "Count"]
        # Determine manufacturer based on processor name: AMD processors will be red, Intel processors blue, others gray.
        cpu_counts["Manufacturer"] = cpu_counts["Processor"].apply(
            lambda x: "AMD" if "AMD" in x else ("Intel" if "Intel" in x else "Other")
        )
        fig_cpu = px.bar(
            cpu_counts,
            x="Processor",
            y="Count",
            color="Manufacturer",
            title="5 Most Popular CPUs from Submissions",
            labels={"Count": "Number of Submissions"},
            color_discrete_map={"AMD": "red", "Intel": "lightblue", "Other": "gray"}
        )
        fig_cpu.update_yaxes(dtick=1)  # Set y-axis ticks to integers
        container.plotly_chart(fig_cpu, use_container_width=True)
    else:
        container.info("No submission data yet for CPU popularity.")


# Initially update the CPU graph (if submissions exist)
update_cpu_graph(cpu_graph_container)

# -------------------------------------------
# Main Section: Laptop Specification Form
# -------------------------------------------
st.header("Enter Laptop Specifications")

# Define selection options.
brands_options = ["Razer", "Asus", "Lenovo", "Acer", "Dell", "Microsoft", "HP", "Samsung", "MSI"]
processors_options = ["AMD Ryzen 7", "Intel i5", "Intel i3", "AMD Ryzen 3", "AMD Ryzen 9", "AMD Ryzen 5", "Intel i9",
                      "Intel i7"]
rams_options = [4, 8, 16, 32, 64]
storages_options = ["1TB SSD", "2TB SSD", "256GB SSD", "1TB HDD", "512GB SSD"]
gpus_options = ["Nvidia RTX 3080", "Nvidia RTX 3060", "AMD Radeon RX 6600", "Nvidia RTX 2060", "AMD Radeon RX 6800",
                "Nvidia GTX 1650", "Integrated"]
screen_sizes_options = [13.3, 14, 15.6, 16, 17.3]
resolutions_options = ["1366x768", "1920x1080", "2560x1440", "3840x2160"]
oss_options = ["Linux", "FreeDOS", "Windows"]

brand = st.selectbox("Brand", brands_options)
processor = st.selectbox("Processor", processors_options)
ram = st.selectbox("RAM (GB)", rams_options)
storage = st.selectbox("Storage", storages_options)
gpu = st.selectbox("GPU", gpus_options)
screen_size = st.selectbox("Screen Size (inches)", screen_sizes_options)
resolution = st.selectbox("Resolution", resolutions_options)
operating_system = st.selectbox("Operating System", oss_options)
battery_life = st.number_input("Battery Life (hours)", min_value=0.0, step=0.1)
weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)


def save_submission(record):
    df_new = pd.DataFrame([record])
    if os.path.exists(SUBMISSIONS_FILE):
        df_new.to_csv(SUBMISSIONS_FILE, mode='a', index=False, header=False)
    else:
        df_new.to_csv(SUBMISSIONS_FILE, mode='w', index=False, header=True)


if st.button("Submit"):
    # Construct the payload with keys expected by your model.
    payload = {
        "Inputs": {
            "input1": [
                {
                    "Brand": brand,
                    "Processor": processor,
                    "RAM_GB": ram,
                    "Storage": storage,
                    "GPU": gpu,
                    "Screen_Size_inch": screen_size,
                    "Resolution": resolution,
                    "Battery_Life_hours": battery_life,
                    "Weight_kg": weight,
                    "Operating_System": operating_system,
                    "Price_$": None  # Price to be predicted.
                }
            ]
        },
        "GlobalParameters": {}
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + API_KEY
    }

    try:
        response = requests.post(API_URL, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            result = response.json()
            # Extract the predicted price from the response.
            predicted_value = result["Results"]["WebServiceOutput0"][0]["Scored Labels"]
            st.success(f"Predicted Price: ${predicted_value:,.2f}")
        else:
            st.error("Error: " + str(response.status_code))
            st.text(response.text)
    except Exception as e:
        st.error(f"An error occurred: {e}")

    # Save the form submission.
    submission_record = {
        "Brand": brand,
        "Processor": processor,
        "RAM_GB": ram,
        "Storage": storage,
        "GPU": gpu,
        "Screen_Size_inch": screen_size,
        "Resolution": resolution,
        "Battery_Life_hours": battery_life,
        "Weight_kg": weight,
        "Operating_System": operating_system
    }
    save_submission(submission_record)

    # Update the CPU popularity graph.
    update_cpu_graph(cpu_graph_container)
