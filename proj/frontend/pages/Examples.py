import streamlit as st

def load_examples():


    examples = [
        {
            "Prompt": "Are any of my medicines going out of date?",
            "Description": "Checks the expiry dates of all medicines in inventory and lists the ones expiring soon."
        },
        {
            "Prompt": "Create new order for Paracetamol, quantity 500",
            "Description": "Creates a new order for a specified product with the provided quantity."
        },
        {
            "Prompt": "What stock is running low?",
            "Description": "Lists products in inventory with stock below a predefined threshold."
        },
        {
            "Prompt": "Change category of Aspirin from 'General' to 'OTC'",
            "Description": "Updates the category of a product in the inventory."
        },
        {
            "Prompt": "What is the date of my order for midodrine hydrochloride?",
            "Description": "Fetches the date for an order placed for a specific product."
        },
        {
            "Prompt": "Show me all prescription medications.",
            "Description": "Lists all products in the inventory categorised as prescription medicines."
        },
        {
            "Prompt": "List all products expiring in the next month.",
            "Description": "Fetches details of all batches that are expiring within the next 30 days."
        },
        {
            "Prompt": "Delete order #87 from the system.",
            "Description": "Deletes the order with the specified ID from the orders database."
        },
        {
            "Prompt": "Update stock level for Paracetamol to 200 units.",
            "Description": "Modifies the inventory to update the stock count of the specified product."
        },
        {
            "Prompt": "What is the most popular product based on orders?",
            "Description": "Fetches the product that has been ordered the most times in the system."
        }
    ]


    for example in examples:
        st.markdown(
            f"""
            <div style="border: 1px solid #ddd; border-radius: 5px; padding: 10px; margin: 10px 0;">
                <p><b>Prompt:</b> {example['Prompt']}</p>
                <p><b>Description:</b> {example['Description']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )



st.title("Examples")
st.subheader("Discover different prompts and their uses")
load_examples()
