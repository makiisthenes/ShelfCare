# Conda environment: gemma python==3.11 v.
# Natural Language 2 SQL (NL2SQL) Query Tool.
# Gemma 2 Fine-tuned for Function Calling,
#  https://medium.com/@malumbea/function-tool-calling-using-gemma-transform-instruction-tuned-it-model-bc8b05585377
# https://huggingface.co/DiTy/gemma-2-9b-it-function-calling-GGUF
# Langchain seems to already have a SQLDatabase Toolkit.
# https://python.langchain.com/docs/integrations/tools/sql_database/
# Import the necessary modules from langchain for running local model with Ollama agent,
# Based on documentation on: https://python.langchain.com/v0.1/docs/guides/development/local_llms/
# localhost:11434 (Ollama).
from typing import Dict, Any, List

# Import the necessary modules from langchain for the agent to work properly.

from langchain.agents import Tool, create_react_agent, AgentExecutor
from langchain_community.tools import HumanInputRun
from langchain import hub

# Will also run on Google Vertex AI platform.

# Will run on Google AI Studio.
from dotenv import load_dotenv
import os

# LLM Imports.
from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaLLM

from proj.backend.func_tools import DB_OverviewTool, AddProductTool, DatetimeTool
from proj.chain.tools.date_tool import get_current_date_tool
# from backend.func_tools import AddProductTool
from proj.chain.tools.nl_2_sql import get_database_chain
# import schemas and tools from user defined space.

import logging

from utils import get_credentials_path

logging.getLogger("httpx").setLevel(logging.WARNING)



# Load the environmental variables into the system.
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = get_credentials_path()

# Loaded LLM Models.
# oai_llm = ChatOpenAI(
# 		model="gpt-4o",
# 		temperature=0,
# 		max_tokens=None,
# 		timeout=None,
# 		max_retries=2,
# 	)

# Try using local LLM model. (gemma-2-9B-it-function-calling-Q6_K.gguf)
# We have created the custom model on our PC, named gemma2-ft9
gm_llm = OllamaLLM(
	# model="gemma2-ft9",
	model="gemma2-ft2-structured",  # https://huggingface.co/bastienp/Gemma-2-2B-Instruct-structured-output
	temperature=0,
)
selected_llm = gm_llm

# Prompt for Agent.


# Tools will be performed by the database agent.
def text_to_sql_database_tool(prompt: str) -> str:
	"""Convert text to SQL and execute database query."""
	try:
		db_chain = get_database_chain(selected_llm)
		result = db_chain.invoke({"question": prompt})
		logging.info(f"Database query result: {result}")
		return result
	except Exception as e:
		return f"Error executing database query: {str(e)}"


# Tool Defining
def execute_agent_tools(prompt: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
	"""Execute agent tools with error handling and input validation."""
	tools = [
		Tool.from_function(
			text_to_sql_database_tool,
			return_direct=False,
			name="Pass User Query to Text to SQL Database Tool",
			description="This tool should be used when you need to obtain information from the database related to orders, products and product expiry."
			            " you know relates to a database query like products, orders or product expiry, that no other tool can answer,"
			            "Ths input should be a user queru and NOT a SQL query, please ensure the input is passthrough user query."
			            "This function takes one input, the user query and returns the output of the query, if successful, if not returns an empty string."
			            ""
			            "If an error occurs, pass the error message along with the initial input to resolve the issue."
		),
		DB_OverviewTool,
		# https://python.langchain.com/api_reference/community/tools/langchain_community.tools.human.tool.HumanInputRun.html
		# This is a tool that allows for human input to be run.
		Tool.from_function(
			HumanInputRun().run,
			name="Human Input",
			description="Use this tool when you need to ask the human for additional information or clarification. "
			            "The input should be a question or prompt for the human. "
			            "For example, if you need to know the quantity for a product, you might input 'What quantity should be added?'"
		),
		AddProductTool,
		DatetimeTool,
	]

	# Modified prompt template to handle general queries
	prompt_template = hub.pull("hwchase17/react-chat")  # Using chat version instead

	agent = create_react_agent(selected_llm, tools, prompt_template)
	agent_executor = AgentExecutor(
		agent=agent,
		tools=tools,
		handle_parsing_errors=True,  # Enable error handling
		max_iterations=20,  # Limit iterations to prevent infinite loops
		early_stopping_method="generate",  # Stop early if we can't make progress
		verbose=True,  # Enable verbose logging
		return_intermediate_steps=True,  # This can help with debugging
	)

	# Initialise chat history if not provided
	if chat_history is None:
		chat_history = []

	try:
		# Add basic input validation
		if not prompt or len(prompt.strip()) == 0:
			return {"output": "Please provide a valid input."}

		if len(prompt.strip()) < 3:  # For very short inputs
			return {"output": "Could you please provide more details about what you'd like to know?"}

		# Add the current user input to chat history
		chat_history.append({"role": "user", "content": prompt})

		# Invoke the agent with prompt and chat history
		result = agent_executor.invoke(
			{
				"input": prompt,
				"chat_history": chat_history
			}
		)

		# If the agent returns successfully, append the assistant's response to chat history
		if isinstance(result, dict):
			chat_history.append({"role": "assistant", "content": result.get("output", "")})

		return result if isinstance(result, dict) else {"output": str(result)}

	except Exception as e:
		return {
			"output": f"I'm having trouble processing that request. Could you please rephrase it? Error: {str(e)}",
			"error": True,
			"error_type": type(e).__name__
		}


if __name__ == "__main__":
	while True:
		try:
			prompt = input("Enter a prompt (or 'exit' to quit): ")
			if prompt.lower() == 'exit':
				break

			print("Prompt: ", prompt)
			response = execute_agent_tools(prompt)

			# Handle the response output
			if isinstance(response, dict) and "output" in response:
				print("Response: ", response["output"])
			else:
				print("Response: Something went wrong. Please try again.")

		except KeyboardInterrupt:
			print("\nExiting...")
			break
		except Exception as e:
			print(f"An error occurred: {str(e)}")
# Exit.


# Generate the SQL query.

# prompt = "Show me the products with the highest stock."
# prompt = "What medication do I need to reorder"
# prompt = "Add new medication 'Aspirin' to inventory with stock level 100, category 'General'"
# prompt = "give me a list of products that are medicines?"

# response = text_to_sql_database_tool(prompt)
# print("Response: ", response)
# exit()

# print("Prompt Used: ", prompt)

# query = generate_better_sql_query_chain(prompt, gm_llm)
# print("SQL Query: ", query)
# result = execute_sql_query(query)
# print("Result: ", result)

# # LLM rephrasing.
# rephrased = rephrase_db_results(prompt, str(query), str(result), gm_llm)
# print("Rephrased: ", rephrased)


