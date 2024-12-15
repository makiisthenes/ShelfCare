from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, TypeVar, Generic, Type
from contextlib import contextmanager
from dotenv import load_dotenv
import logging
import os

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')


# Database Manager Singleton...

class DatabaseManager:
	_instance = None
	_engine = None
	_SessionFactory = None

	def __new__(cls):
		if cls._instance is None:
			cls._instance = super(DatabaseManager, cls).__new__(cls)
			# Initialize the connection when instance is created
			cls._instance._initialize_connection()
		return cls._instance

	def _initialize_connection(self):
		"""Initialize the database connection using environment variables"""
		if not self._engine:
			try:
				# {os.getenv('DB_PASSWORD')}
				connection_string = f"mysql://{os.getenv('DB_USER')}:@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
				print("Connection String: ", connection_string)
				self._engine = create_engine(
					connection_string,
					pool_pre_ping=True,  # Enables connection health checks
					pool_size=5,  # Maximum number of permanent connections
					max_overflow=10  # Maximum number of temporary connections
				)
				self._SessionFactory = sessionmaker(bind=self._engine)
				logger.info("Database connection initialized successfully")
			except Exception as e:
				logger.error(f"Failed to initialize database connection: {str(e)}")
				raise

	@contextmanager
	def session(self):
		"""Provide a transactional scope around a series of operations."""
		if not self._SessionFactory:
			raise RuntimeError("DatabaseManager not initialized properly")

		session = self._SessionFactory()
		try:
			yield session
			session.commit()
		except Exception as e:
			session.rollback()
			logger.error(f"Session error: {str(e)}")
			raise
		finally:
			session.close()

	def get_by_id(self, model: Type[T], id: int) -> Optional[T]:
		"""Generic method to get an entity by ID"""
		try:
			with self.session() as session:
				return session.get(model, id)
		except SQLAlchemyError as e:
			logger.error(f"Error fetching {model.__name__} with id {id}: {str(e)}")
			return None

	def create(self, entity: T) -> Optional[T]:
		"""Generic method to create an entity"""
		try:
			with self.session() as session:
				session.add(entity)
				session.commit()
				session.refresh(entity)
				return entity
		except SQLAlchemyError as e:
			logger.error(f"Error creating {type(entity).__name__}: {str(e)}")
			return None

	def update(self, entity: T) -> Optional[T]:
		"""Generic method to update an entity"""
		try:
			with self.session() as session:
				session.merge(entity)
				session.commit()
				return entity
		except SQLAlchemyError as e:
			logger.error(f"Error updating {type(entity).__name__}: {str(e)}")
			return None

	def delete(self, entity: T) -> bool:
		"""Generic method to delete an entity"""
		try:
			with self.session() as session:
				session.delete(entity)
				session.commit()
				return True
		except SQLAlchemyError as e:
			logger.error(f"Error deleting {type(entity).__name__}: {str(e)}")
			return False

	def execute_query(self, query: str, params: dict = None):
		"""Execute a raw SQL query"""
		try:
			with self.session() as session:
				result = session.execute(text(query), params or {})
				return result.fetchall()
		except SQLAlchemyError as e:
			logger.error(f"Error executing query: {str(e)}")
			return None


# Example usage
if __name__ == "__main__":
	from model_schema import Product, Order, ProductExpiry

	try:
		# Get database instance (it will automatically initialize using env variables)
		db = DatabaseManager()

		# Example operations
		new_product = Product(
			product_name="Test Product",
			supplier="Test Supplier",
			category="Test",
			stock_count=100,
			cost=10.99,
			description="Created with SQLAlchemy instead of mysql flakey operation."
		)
		created_product = db.create(new_product)

	except Exception as e:
		logger.error(f"Error in example operations: {str(e)}")