from flask import Flask, jsonify
from flask_cors import CORS
from database_orm import DatabaseManager
from model_schema import Product, Order, ProductExpiry
from sqlalchemy import select
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize database manager
db = DatabaseManager()


@app.get("/inventory")
def get_inventory():
	"""Return the current inventory as a JSON object"""
	try:
		with db.session() as session:
			# Create query to get all products
			query = select(Product)
			products = session.execute(query).scalars()

			# Convert products to list of dictionaries
			inventory_data = [{
				"id": product.id,
				"product_name": product.product_name,
				"supplier": product.supplier,
				"category": product.category,
				"stock_count": product.stock_count,
				"cost": float(product.cost) if product.cost else None,
				"description": product.description
			} for product in products]

			return jsonify(inventory_data), 200

	except Exception as e:
		logger.error(f"Error fetching inventory: {str(e)}")
		return jsonify({"error": "Failed to fetch inventory data"}), 500


@app.get("/orders")
def get_orders():
	"""Return the current orders as a JSON object"""
	try:
		with db.session() as session:
			# Create query to get all orders with product information
			query = select(Order).join(Product)
			orders = session.execute(query).scalars()

			# Convert orders to list of dictionaries
			orders_data = [{
				"order_id": order.order_id,
				"product_id": order.product_id,
				"order_date": order.order_date.isoformat() if order.order_date else None,
				"quantity": order.quantity,
				"date_expected": order.date_expected.isoformat() if order.date_expected else None,
				# Including product name for reference
				"product_name": order.product.product_name if order.product else None
			} for order in orders]

			return jsonify(orders_data), 200

	except Exception as e:
		logger.error(f"Error fetching orders: {str(e)}")
		return jsonify({"error": "Failed to fetch orders data"}), 500



@app.get("/expiry")
def get_expiry():
    """Return the expiry data as a JSON object"""
    try:
        with db.session() as session:
            # Query the expiry table with product information
            query = select(ProductExpiry).join(Product)
            expiry_data = session.execute(query).scalars()

            # Convert expiry data to a list of dictionaries
            expiry_list = [{
                "batch_id": expiry.id,
                "product_id": expiry.product_id,
                "product_name": expiry.product.product_name if expiry.product else None,
                "expiry_date": expiry.expiry_date.isoformat(),
                "quantity": expiry.quantity
            } for expiry in expiry_data]

            return jsonify(expiry_list), 200

    except Exception as e:
        logger.error(f"Error fetching expiry data: {str(e)}")
        return jsonify({"error": "Failed to fetch expiry data"}), 500




# Error handlers
@app.errorhandler(404)
def not_found_error(error):
	return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(500)
def internal_error(error):
	return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
	app.run(debug=True, port=5000)
