from datetime import datetime, timedelta

from langchain.agents import Tool
from dotenv import load_dotenv
from sqlalchemy import select, func, and_

from proj.backend.database_orm import DatabaseManager
from proj.backend.model_schema import Product, ProductExpiry
from proj.backend.tool_schema import ProductSchema, DBOverviewSchema
from proj.chain.tools.date_tool import get_current_date_tool

load_dotenv()

# Initialize database manager as a singleton
db = DatabaseManager()


def add_product(product: ProductSchema) -> str:
	"""Add a new product to the database using SQLAlchemy ORM."""
	try:
		# Input validation
		if not product.product_name or len(product.product_name) > 100:
			return "Product name is invalid, or more than 100 characters."
		if product.supplier and len(product.supplier) > 100:
			return "Supplier name is invalid and or is more than 100 characters."
		if not product.category or len(product.category) > 18:
			return "Error with category, or category is more than 18 characters."

		# Create new product instance using SQLAlchemy model
		new_product = Product(
			product_name=product.product_name,
			supplier=product.supplier,
			category=product.category,
			stock_count=product.stock_count,
			cost=product.cost,
			description=product.description
		)

		# Use database manager to create the product
		result = db.create(new_product)

		if result:
			return "Product added successfully to the database."
		else:
			return "Failed to add product to the database."

	except Exception as e:
		return f"An error occurred while adding the product to the database, Error: {e}"


def get_db_overview(query: DBOverviewSchema) -> str:
	"""
	Get database overview using SQLAlchemy ORM.
	Returns product count, total count and expired quantity for given days.
	"""
	try:
		with db.session() as session:
			# Calculate date range
			try:
				if isinstance(query, str):
					days = int(query)
					if days < 0:
						days = 7
				if not query.days:
					days = 7
				else:
					days = query.days
			except ValueError:
				days = 7
			current_date = datetime.now().date()
			future_date = current_date + timedelta(days=days)

			# Query for products count and total stock
			products_query = select(
				func.count(Product.id).label('product_count'),
				func.sum(Product.stock_count).label('total_count')
			)
			products_result = session.execute(products_query).first()

			# Query for expired quantity
			expired_query = select(
				func.sum(ProductExpiry.quantity)
			).where(
				and_(
					ProductExpiry.expiry_date >= current_date,
					ProductExpiry.expiry_date <= future_date
				)
			)
			expired_quantity = session.execute(expired_query).scalar() or 0

			# Format the response
			return (
				f"The database overview for the last {days} days is as follows:\n"
				f"Product Count: {products_result.product_count or 0}\n"
				f"Total Count: {products_result.total_count or 0}\n"
				f"Expired Quantity: {expired_quantity}"
			)

	except Exception as e:
		return f"Error occurred while fetching database overview. {e}"


# Once all functions are converted, do the following,
DB_OverviewTool = Tool.from_function(
	get_db_overview,
	return_direct=False,  # always false for db outputs.
	args_schema=DBOverviewSchema,
	name="High Level (Basic) Overview Tool",  # give it a very useful name...
	description="This tool should be ONLY be used when the user explicitly requests an overview which including number of days to span,"
	            "If a user is asking for data basic abstract information. "
				"This function takes one input, the number of days to span, if no days are mentioned default to 7 days."
				"This functions returns information about total product count, total count and expired quantity, so only request this when one of these three are needed..."
)

AddProductTool = Tool.from_function(
	add_product,
	return_direct=False,
	args_schema=ProductSchema,
	name="Add Product Tool",
	description="This tool should be used when you need to add a product to the database."
				"This function takes in the product name, supplier, category, stock count, cost and description."
				"This function returns a message if the product was added successfully or not."
)

DatetimeTool = Tool.from_function(
	get_current_date_tool,
	return_direct=False,
	args_schema=None,
	name="Get Current Date Tool",
	description="This tool should be used when you need to get the current date."
)



# if __name__ == "__main__":
# 	response = add_product(ProductSchema(
# 		product_name="Test Product",
# 		supplier="Test Supplier",
# 		category="Test Cate",
# 		stock_count=100,
# 		cost=1.99,
# 		description="Test Description"
# 	))
# 	print(response)



# Continue here...
#
#
# @app.route('/tables', methods=['GET'])
# def show_tables():
# 	try:
# 		if not conn or not cursor:
# 			raise Exception("Database connection is not established")
#
# 		cursor.execute("SHOW TABLES")
# 		tables = cursor.fetchall()
# 		data = [table[0] for table in tables]
#
# 		return jsonify(data), 200
#
# 	except Exception as e:
# 		return jsonify({"error": str(e)}), 500
#
#
# @app.route('/api/getProducts', methods=['GET'])
# def getProducts():
# 	try:
# 		if not conn or not cursor:
# 			raise Exception("Database connection is not established")
#
# 		cursor.callproc('getProducts')
# 		query_results = cursor.stored_results()
# 		data = []
#
# 		for result in query_results:
# 			for row in result.fetchall():
# 				data.append({
# 					"id": row[0],
# 					"product_name": row[1],
# 					"category": row[2],
# 					"stock_count": row[3],
# 					"cost": row[4],
# 					"description": row[5]
# 				})
#
# 		return jsonify(data), 200
#
# 	except Exception as e:
# 		return jsonify({"error": str(e)}), 500
#
#
# @app.route('/api/getProductsExpiry', methods=['GET'])
# def getProductsExpiry():
# 	try:
# 		if not conn or not cursor:
# 			raise Exception("Database connection is not established")
#
# 		cursor.callproc('getProductExpiry')
# 		query_results = cursor.stored_results()
# 		data = []
#
# 		for result in query_results:
# 			for row in result.fetchall():
# 				data.append({
# 					"id": row[0],
# 					"expiry_date": row[1],
# 					"quantity": row[2]
# 				})
#
# 		return jsonify(data), 200
#
# 	except Exception as e:
# 		return jsonify({"error": str(e)}), 500
#
#
# @app.route('/api/getOrders', methods=['GET'])
# def getOrders():
# 	try:
# 		if not conn or not cursor:
# 			raise Exception("Database connection is not established")
#
# 		cursor.callproc('getOrders')
# 		query_results = cursor.stored_results()
# 		data = []
#
# 		for result in query_results:
# 			for row in result.fetchall():
# 				data.append({
# 					"order_id": row[0],
# 					"product_id": row[1],
# 					"order_date": row[2],
# 					"quantity": row[3],
# 					"date_expected": row[4]
# 				})
#
# 		return jsonify(data), 200
#
# 	except Exception as e:
# 		return jsonify({"error": str(e)}), 500
#
#

#
#
# @app.route('/api/addProductExpiry', methods=['POST'])
# def addProductExpiry():
# 	i_id = request.json.get('id')
# 	i_expiry_date = request.json.get('expiry_date')
# 	i_quantity = request.json.get('quantity')
#
# 	try:
# 		if not isinstance(i_id, int):
# 			i_id = int(i_id)
# 		if not isinstance(i_quantity, int):
# 			i_quantity = int(i_quantity)
# 		i_expiry_date = datetime.strptime(i_expiry_date, '%a, %d %b %Y %H:%M:%S GMT').strftime('%Y-%m-%d')
#
# 	except ValueError:
# 		return jsonify({"error": "Invalid data types provided"}), 400
#
# 	try:
# 		cursor.callproc('insertExpiryDate', [
# 			i_id,
# 			i_expiry_date,
# 			i_quantity
# 		])
# 		conn.commit()
# 		return jsonify({"message": "Product Expiry added successfully"}), 200
#
# 	except Exception as e:
# 		return jsonify({"error": str(e)}), 500
#
#
# @app.route('/api/addOrder', methods=['POST'])
# def addOrder():
# 	i_product_id = request.json.get('product_id')
# 	i_quantity = request.json.get('quantity')
#
# 	try:
#
# 		if not isinstance(i_product_id, int):
# 			i_product_id = int(i_product_id)
# 		if not isinstance(i_quantity, int):
# 			i_quantity = int(i_quantity)
#
#
#
# 	except ValueError:
# 		return jsonify({"error": "Invalid data types provided"}), 400
#
# 	try:
# 		cursor.callproc('insertOrder', [
# 			i_product_id,
# 			i_quantity
# 		])
# 		conn.commit()
# 		return jsonify({"message": "order added successfully"}), 200
#
# 	except Exception as e:
# 		return jsonify({"error": str(e)}), 500
#
#
# @app.route('/api/updateProduct', methods=['POST'])
# def updateProduct():
# 	i_id = request.json.get('id')
# 	i_product_name = request.json.get('product_name')
# 	i_supplier = request.json.get('supplier')
# 	i_category = request.json.get('category')
# 	i_stock_count = request.json.get('stock_count')
# 	i_cost = request.json.get('cost')
# 	i_description = request.json.get('description')
#
# 	try:
# 		if not isinstance(i_id, int):
# 			i_id = int(i_id)
# 		if not i_product_name or len(i_product_name) > 100:
# 			return jsonify({"error": "Invalid product name"}), 400
# 		if i_supplier and len(i_supplier) > 100:
# 			return jsonify({"error": "Invalid supplier name"}), 400
# 		if not i_category or len(i_category) > 12:
# 			return jsonify({"error": "Invalid category"}), 400
# 		if not isinstance(i_stock_count, int):
# 			i_stock_count = int(i_stock_count)
# 		if not isinstance(i_cost, float) and not isinstance(i_cost, int):
# 			i_cost = float(i_cost)
#
# 	except ValueError:
# 		return jsonify({"error": "Invalid data types provided"}), 400
#
# 	try:
# 		cursor.callproc('updateProduct', [
# 			i_id,
# 			i_product_name,
# 			i_supplier,
# 			i_category,
# 			i_stock_count,
# 			i_cost,
# 			i_description
# 		])
# 		conn.commit()
# 		return jsonify({"message": "Product updated successfully"}), 200
#
# 	except Exception as e:
# 		return jsonify({"error": str(e)}), 500
#
#
# @app.route('/api/updateProductExpiry', methods=['POST'])
# def updateProductExpiry():
# 	i_id = request.json.get('id')
# 	i_expiry_date = request.json.get('expiry_date')
# 	i_quantity = request.json.get('quantity')
#
# 	try:
# 		if not isinstance(i_id, int):
# 			i_id = int(i_id)
# 		if not isinstance(i_quantity, int):
# 			i_quantity = int(i_quantity)
# 		i_expiry_date = datetime.strptime(i_expiry_date, '%a, %d %b %Y %H:%M:%S GMT').strftime('%Y-%m-%d')
#
# 	except ValueError:
# 		return jsonify({"error": "Invalid data types provided"}), 400
#
# 	try:
# 		cursor.callproc('updateProductExpiry', [
# 			i_id,
# 			i_expiry_date,
# 			i_quantity
# 		])
# 		conn.commit()
# 		return jsonify({"message": "Product Expiry updated successfully"}), 200
#
# 	except Exception as e:
# 		return jsonify({"error": str(e)}), 500
#
#
# @app.route('/api/updateOrder', methods=['POST'])
# def updateOrder():
# 	i_order_id = request.json.get('order_id')
# 	i_product_id = request.json.get('product_id')
# 	i_quantity = request.json.get('quantity')
#
# 	try:
# 		if not isinstance(i_order_id, int):
# 			i_order_id = int(i_order_id)
# 		if not isinstance(i_product_id, int):
# 			i_product_id = int(i_product_id)
# 		if not isinstance(i_quantity, int):
# 			i_quantity = int(i_quantity)
#
#
#
# 	except ValueError:
# 		return jsonify({"error": "Invalid data types provided"}), 400
#
# 	try:
# 		cursor.callproc('updateOrder', [
# 			i_order_id,
# 			i_product_id,
# 			i_quantity
# 		])
# 		conn.commit()
# 		return jsonify({"message": "order updated successfully"}), 200
#
# 	except Exception as e:
# 		return jsonify({"error": str(e)}), 500
#
#
# @app.route('/api/removeProduct/<int:product_id>', methods=['DELETE'])
# def removeProduct(product_id: int):
# 	try:
#
# 		cursor.callproc('deleteProduct', [product_id])
# 		conn.commit()
# 		return jsonify({"message": f"Product with ID {product_id} removed successfully."}), 200
#
# 	except Exception as e:
# 		return jsonify({"error": str(e)}), 500
#
#
# @app.route('/api/removeProductExpiry/<int:product_id>', methods=['DELETE'])
# def removeProductExpiry(product_id: int):
# 	try:
#
# 		cursor.callproc('deleteProductExpiry', [product_id])
# 		conn.commit()
# 		return jsonify({"message": f"Product with ID {product_id} removed successfully from product expiry."}), 200
#
# 	except Exception as e:
# 		return jsonify({"error": str(e)}), 500
#
#
# @app.route('/api/removeOrder/<int:order_id>', methods=['DELETE'])
# def removeOrder(order_id: int):
# 	try:
#
# 		cursor.callproc('deleteOrder', [order_id])
# 		conn.commit()
# 		return jsonify({"message": f"Order with ID {order_id} removed successfully"}), 200
#
# 	except Exception as e:
# 		return jsonify({"error": str(e)}), 500
#
#
# @app.route('/api/showStock', methods=['GET'])
# def show_stock():
# 	try:
# 		if not conn or not cursor:
# 			raise Exception("Database connection is not established")
#
# 		cursor.callproc('showStock')
# 		query_results = cursor.stored_results()
# 		data = []
#
# 		for result in query_results:
# 			for row in result.fetchall():
# 				data.append({
# 					"id": row[0],
# 					"product_name": row[1],
# 					"supplier": row[2],
# 					"category": row[3],
# 					"stock_count": row[4],
# 					"cost": row[5],
# 					"description": row[6],
# 					"expiry_date": row[7],
# 					"quantity": row[8]
# 				})
#
# 		return jsonify(data), 200
#
# 	except Exception as e:
# 		return jsonify({"error": str(e)}), 500
#
#
# @app.route('/api/showLowStock/<int:num>', methods=['GET'])
# def showLowStock(num: int):
# 	try:
# 		if not conn or not cursor:
# 			raise Exception("Database connection is not established")
#
# 		cursor.callproc('showLowStock', [num])
# 		query_results = cursor.stored_results()
# 		data = []
#
# 		for result in query_results:
# 			for row in result.fetchall():
# 				data.append({
# 					"id": row[0],
# 					"product_name": row[1],
# 					"supplier": row[2],
# 					"category": row[3],
# 					"stock_count": row[4],
# 					"cost": row[5],
# 					"description": row[6],
# 					"expiry_date": row[7],
# 					"quantity": row[8]
# 				})
#
# 		return jsonify(data), 200
#
# 	except Exception as e:
# 		return jsonify({"error": str(e)}), 500
#
#
# @app.route('/api/showExpired', methods=['GET'])
# def showExpired():
# 	try:
# 		if not conn or not cursor:
# 			raise Exception("Database connection is not established")
#
# 		cursor.callproc('checkExpiredItems')
# 		query_results = cursor.stored_results()
# 		data = []
#
# 		for result in query_results:
# 			for row in result.fetchall():
# 				data.append({
# 					"id": row[0],
# 					"product_name": row[1],
# 					"supplier": row[2],
# 					"category": row[3],
# 					"cost": row[4],
# 					"expiry_date": row[5],
# 					"quantity": row[6]
# 				})
#
# 		return jsonify(data), 200
#
# 	except Exception as e:
# 		return jsonify({"error": str(e)}), 500
#
#
# @app.route('/api/showExpiring/<int:days>', methods=['GET'])
# def showExpiring(days: int):
# 	try:
# 		if not conn or not cursor:
# 			raise Exception("Database connection is not established")
#
# 		cursor.callproc('checkExpiringItems', [days])
# 		query_results = cursor.stored_results()
# 		data = []
#
# 		for result in query_results:
# 			for row in result.fetchall():
# 				data.append({
# 					"id": row[0],
# 					"product_name": row[1],
# 					"supplier": row[2],
# 					"category": row[3],
# 					"cost": row[4],
# 					"expiry_date": row[5],
# 					"quantity": row[6]
# 				})
#
# 		return jsonify(data), 200
#
# 	except Exception as e:
# 		return jsonify({"error": str(e)}), 500
#
#
# @app.route('/api/orderLowStock', methods=['POST'])
# def order_low_stock():
# 	num = request.json.get('num')
# 	order_quantity = request.json.get('quantity')
#
# 	if num is None or order_quantity is None:
# 		return jsonify({"error": "Missing parameter"}), 400
#
# 	try:
#
# 		cursor.callproc('orderLowStockItems', [num, order_quantity])
# 		conn.commit()
# 		return jsonify({"message": "Low stock items ordered"}), 200
#
# 	except Exception as e:
# 		return jsonify({"error": str(e)}), 500
#
#
# @app.route('/api/orderExpiring/<int:days>', methods=['POST'])
# def order_expirying_items(days: int):
# 	if days is None:
# 		return jsonify({"error": "Missing parameter"}), 400
#
# 	try:
#
# 		cursor.callproc('orderExpiringItems', [days])
# 		conn.commit()
# 		return jsonify({"message": f"ordering items expirying in {days} days"}), 200
#
# 	except Exception as e:
# 		return jsonify({"error": str(e)}), 500
#
#
# @app.route('/api/orderExpired', methods=['POST'])
# def order_expired_items():
# 	try:
#
# 		cursor.callproc('orderExpiredItems')
# 		conn.commit()
# 		return jsonify({"message": f"ordering expired items"}), 200
#
# 	except Exception as e:
# 		return jsonify({"error": str(e)}), 500
#
#
