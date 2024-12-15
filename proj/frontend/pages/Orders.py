import requests
import os
import streamlit as st
import datetime


def load_orders():

    flask_api_url = "http://127.0.0.1:5000/orders"
    response = requests.get(flask_api_url)

    if response.status_code == 200:
        orders_data = response.json()
        if orders_data:
            st.dataframe(orders_data)
        else:
            st.write("No order data found.")
    else:
        st.error("Failed to fetch orders data from Flask backend.")


st.header("Orders")
st.subheader("View current orders")
load_orders()