import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import re
import os
import time  # For animation delays

from authentication import login_signup

st.set_page_config(layout='wide')

# Initialize session state variables if they don't exist.
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""

# If not logged in, show the login/signup form.
if not st.session_state.authenticated:
    login_signup()
    # If the user just logged in, immediately reload the app.
    if st.session_state.authenticated:
        if hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
        else:
            st.write("Please, click again on Log In button.")
    else:
        st.stop()

# If logged in, show the main application.

# Top right logout button
col1, col2 = st.columns([4, 1])
with col2:
    st.markdown(f"**Logged in as: {st.session_state.username}**")
    if st.button("Log Out"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        if hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
        else:
            st.write("Please, click again on Log Out button.")

API_URL = 'http://060fd6ad-695f-4ef8-a9b2-24f8243c2f3d.eastus2.azurecontainer.io/score'
API_KEY = 'aMv3SZnrX4pkyuwhigofZ3mRG2dvhS2B'  # Replace with your actual API key if needed

SUBMISSIONS_FILE = "submissions.csv"

st.title("Laptop Specification Form & Price Predictor")
st.markdown(f"""
Welcome **{st.session_state.username}**!

This app predicts the price of a laptop based on your input specifications.
It also saves your submission and displays sidebar graphs based on all users submissions:
- **Average Price by Brand** (each brand in a different color)
- **Price vs. RAM**
- **5 Most Popular CPUs**
- **Operating System Distribution**
- **Battery life based on screen size**

The machine learning model is deployed on Azure Machine Learning.
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

# Sidebar graph: Average Price by Brand
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

# Sidebar graph: Price vs. RAM
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

# Sidebar chart: 5 Most Popular CPUs from Submissions
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

# Sidebar chart: Operating System Distribution (Donut Chart)
os_chart_container = st.sidebar.empty()


def update_os_chart(container):
    if os.path.exists(SUBMISSIONS_FILE):
        submissions_df = pd.read_csv(SUBMISSIONS_FILE)
    else:
        submissions_df = pd.DataFrame()

    if not submissions_df.empty and "Operating_System" in submissions_df.columns:
        os_counts = submissions_df["Operating_System"].value_counts().reset_index()
        os_counts.columns = ["Operating_System", "Count"]
        fig_os = px.pie(
            os_counts,
            values="Count",
            names="Operating_System",
            title="Operating System Distribution",
            color="Operating_System",
            color_discrete_map={
                "Linux": "orange",
                "FreeDOS": "grey",
                "Windows": "lightblue"
            }
        )
        fig_os.update_traces(hole=0.4, hoverinfo="label+percent+name")
        container.plotly_chart(fig_os, use_container_width=True)
    else:
        container.info("No submission data yet for OS distribution.")


update_os_chart(os_chart_container)

battery_chart_container = st.sidebar.empty()

def update_battery_chart(container):
    if os.path.exists(SUBMISSIONS_FILE):
        submissions_df = pd.read_csv(SUBMISSIONS_FILE)
    else:
        submissions_df = pd.DataFrame()

    if not submissions_df.empty and "Battery_Life_hours" in submissions_df.columns and "Screen_Size_inch" in submissions_df.columns:
        fig_battery = px.scatter(
            submissions_df,
            x="Screen_Size_inch",
            y="Battery_Life_hours",
            color="Brand" if "Brand" in submissions_df.columns else None,
            size="Battery_Life_hours",  
            hover_name="Brand" if "Brand" in submissions_df.columns else None,
            title="Battery Life vs. Screen Size",
            labels={"Screen_Size_inch": "Screen Size (inches)", "Battery_Life_hours": "Battery Life (hours)"},
        )

        fig_battery.update_traces(marker=dict(line=dict(width=1, color="black")))  

        container.empty()  
        container.plotly_chart(fig_battery, use_container_width=True, key="battery_chart")
    else:
        container.info("No submission data yet for battery life analysis.")

update_battery_chart(battery_chart_container)

# Define input options
brands_options = ["Acer", "Asus", "Dell", "HP", "Lenovo", "Microsoft", "MSI", "Razer", "Samsung"]
processors_options = ["Intel i3", "Intel i5", "Intel i7", "Intel i9",
                      "AMD Ryzen 3", "AMD Ryzen 5", "AMD Ryzen 7", "AMD Ryzen 9"]
rams_options = [4, 8, 16, 32, 64]
storages_options = ["256GB SSD", "512GB SSD", "1TB SSD", "2TB SSD", "1TB HDD"]
gpus_options = ["Nvidia RTX 3080", "Nvidia RTX 3060", "AMD Radeon RX 6600",
                "Nvidia RTX 2060", "AMD Radeon RX 6800", "Nvidia GTX 1650", "Integrated"]
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
        with st.spinner("Submitting your specs and predicting the price..."):
            response = requests.post(API_URL, data=json.dumps(payload), headers=headers)
            time.sleep(1)  # Simulate a short delay for spinner effect
    except Exception as e:
        st.error(f"An error occurred: {e}")
    else:
        if response.status_code == 200:
            result = response.json()
            # Extract the predicted price from the response.
            try:
                predicted_value = float(result["Results"]["WebServiceOutput0"][0]["Scored Labels"])
            except Exception as e:
                st.error(f"Error parsing prediction result: {e}")
                predicted_value = None

            if predicted_value is not None:
                # Animate the predicted price reveal
                price_placeholder = st.empty()
                steps = 50  # Number of animation steps
                for i in range(steps):
                    animated_price = predicted_value * (i + 1) / steps
                    price_placeholder.markdown(f"**Predicted Price: ${animated_price:,.2f}**")
                    time.sleep(0.05)
                # Ensure the final predicted price is displayed
                price_placeholder.markdown(f"**Predicted Price: ${predicted_value:,.2f}**")
        else:
            st.error("Error: " + str(response.status_code))
            st.text(response.text)

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
    update_os_chart(os_chart_container)
    update_battery_chart(battery_chart_container)
