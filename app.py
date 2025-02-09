import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import re
import os

from authentication import login_signup

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""

if not st.session_state.authenticated:
    login_signup()
    st.stop()

col1, col2 = st.columns([4, 1])
with col2:
    st.markdown(f"**Logged in as: {st.session_state.username}**")
    if st.button("Log Out"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        if hasattr(st, "experimental_rerun"):
            st.experimental_rerun()

API_URL = 'http://060fd6ad-695f-4ef8-a9b2-24f8243c2f3d.eastus2.azurecontainer.io/score'
API_KEY = 'aMv3SZnrX4pkyuwhigofZ3mRG2dvhS2B'  # Replace with your actual API key if needed

SUBMISSIONS_FILE = "submissions.csv"

st.title("Laptop Specification Form & Price Predictor")
st.markdown(f"""
Welcome **{st.session_state.username}**!

This app predicts the price of a laptop based on your input specifications.
It also saves your submission and displays sidebar graphs:
- **Average Price by Brand** (each brand in a different color)
- **Price vs. RAM**
- **5 Most Popular CPUs from Submissions**

The machine learning models are deployed on Azure Machine Learning.
""")


@st.cache_data
def load_data():
    try:
        data = pd.read_csv("laptop.csv")
    except Exception as e:
        st.error(f"Error loading CSV file: {e}")
        return pd.DataFrame()

    if "RAM_GB" in data.columns:
        try:
            if data["RAM_GB"].dtype == object:
                data["RAM_GB"] = data["RAM_GB"].str.extract(r"(\d+)", expand=False)
            data["RAM_GB"] = pd.to_numeric(data["RAM_GB"], errors="coerce")
        except Exception as e:
            st.error(f"Error processing 'RAM_GB': {e}")
    else:
        st.error("Column 'RAM_GB' not found.")

    def convert_storage(s):
        s = str(s)
        match = re.search(r"(\d+(\.\d+)?)", s)
        if match:
            value = float(match.group(1))
            if "TB" in s.upper():
                value *= 1024
            return value
        return None

    if "Storage" in data.columns:
        try:
            data["Storage"] = data["Storage"].apply(convert_storage)
        except Exception as e:
            st.error(f"Error processing 'Storage': {e}")
    else:
        st.error("Column 'Storage' not found.")

    # Process 'Price_$': remove '$' symbols/commas and convert to numeric.
    if "Price_$" in data.columns:
        try:
            data["Price_$"] = data["Price_$"].astype(str).replace({r"\$": "", ",": ""}, regex=True)
            data["Price_$"] = pd.to_numeric(data["Price_$"], errors="coerce")
        except Exception as e:
            st.error(f"Error processing 'Price_$': {e}")
    else:
        st.error("Column 'Price_$' not found.")

    return data

df = load_data()

if "Brand" in df.columns and "Price_$" in df.columns:
    price_by_brand = df.groupby("Brand")["Price_$"].mean().reset_index()
    fig_brand = px.bar(
        price_by_brand,
        x="Brand",
        y="Price_$",
        color="Brand",
        title="Average Price by Brand",
        labels={"Price_$": "Average Price ($)"}
    )
    st.sidebar.plotly_chart(fig_brand, use_container_width=True)
else:
    st.sidebar.error("Required columns for brand analysis not found.")

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

cpu_graph_container = st.sidebar.empty()

def update_cpu_graph(container):
    if os.path.exists(SUBMISSIONS_FILE):
        submissions_df = pd.read_csv(SUBMISSIONS_FILE)
    else:
        submissions_df = pd.DataFrame()

    if not submissions_df.empty and "Processor" in submissions_df.columns:
        cpu_counts = submissions_df["Processor"].value_counts().nlargest(5).reset_index()
        cpu_counts.columns = ["Processor", "Count"]
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
        fig_cpu.update_yaxes(dtick=1)
        container.plotly_chart(fig_cpu, use_container_width=True)
    else:
        container.info("No submission data yet for CPU popularity.")

update_cpu_graph(cpu_graph_container)

brands_options = ["Acer", "Asus", "Dell", "HP", "Lenovo", "Microsoft", "MSI", "Razer", "Samsung"]
processors_options = ["Intel i3","Intel i5","Intel i7", "Intel i9","AMD Ryzen 3","AMD Ryzen 5", "AMD Ryzen 7", "AMD Ryzen 9"]
rams_options = [4, 8, 16, 32, 64]
storages_options = ["256GB SSD","512GB SSD","1TB SSD", "2TB SSD",  "1TB HDD"]
gpus_options = ["Nvidia RTX 3080", "Nvidia RTX 3060", "AMD Radeon RX 6600", "Nvidia RTX 2060", "AMD Radeon RX 6800",
                "Nvidia GTX 1650", "Integrated"]
screen_sizes_options = [13.3, 14, 15.6, 16, 17.3]
resolutions_options = ["1366x768", "1920x1080", "2560x1440", "3840x2160"]
oss_options = ["Linux", "FreeDOS", "Windows"]

st.header("Enter Laptop Specifications")

col1, col2, col3, col4, col5 = st.columns([1.5, 1.5, 1.5, 1.5, 1.5])
with col1:
    brand = st.selectbox("Brand", brands_options)
    storage = st.selectbox("Storage", storages_options)
with col2:
    processor = st.selectbox("Processor", processors_options)
    gpu = st.selectbox("GPU", gpus_options)
with col3:
    ram = st.selectbox("RAM (GB)", rams_options)
    screen_size = st.selectbox("Screen Size (inches)", screen_sizes_options)
with col4:
    resolution = st.selectbox("Resolution", resolutions_options)
    operating_system = st.selectbox("Operating System", oss_options)
with col5:
    battery_life = st.number_input("Battery Life (hours)", min_value=0.0, step=0.1)
    weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)



def save_submission(record):
    df_new = pd.DataFrame([record])
    if os.path.exists(SUBMISSIONS_FILE):
        df_new.to_csv(SUBMISSIONS_FILE, mode="a", index=False, header=False)
    else:
        df_new.to_csv(SUBMISSIONS_FILE, mode="w", index=False, header=True)


if st.button("Submit"):
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
                    "Price_$": None
                }
            ]
        },
        "GlobalParameters": {}
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + API_KEY
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

    update_cpu_graph(cpu_graph_container)
