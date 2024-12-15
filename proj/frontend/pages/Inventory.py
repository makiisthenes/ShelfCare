import requests
import os
import streamlit as st


def load_inventory():

    flask_api_url = "http://127.0.0.1:5000/inventory"
    response = requests.get(flask_api_url)

    if response.status_code == 200:
        inventory_data = response.json()
        if inventory_data:
            st.dataframe(inventory_data)
        else:
            st.write("No inventory data found.")
    else:
        st.error("Failed to fetch inventory data from Flask backend.")


st.header("Inventory")
st.subheader("View current inventory")
load_inventory()
