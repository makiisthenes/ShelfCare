from datetime import datetime


def get_current_date_tool(*args, **kwargs) -> str:
	"""Get the current date as a string"""
	return datetime.now().strftime("%Y-%m-%d")