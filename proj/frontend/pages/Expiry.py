import requests
import streamlit as st


def load_expiry():

    # Flask API URL for expiry endpoint
    flask_api_url = "http://127.0.0.1:5000/expiry"
    response = requests.get(flask_api_url)

    if response.status_code == 200:
        expiry_data = response.json()
        if expiry_data:
            st.dataframe(expiry_data)
        else:
            st.write("No expiry data found.")
    else:
        st.error("Failed to fetch expiry data from Flask backend.")


# Streamlit layout for expiry
st.header("Product Expiry")
st.subheader("View batch expiry details")
load_expiry()
