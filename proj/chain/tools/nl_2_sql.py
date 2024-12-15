# Tracked on Langsmith:
# https://smith.langchain.com/o/f9fcfa57-7f9f-4da8-94e1-dd1ed20582b5/projects/p/d7788b08-51e5-4dd6-b280-946fac174805?timeModel=%7B%22duration%22%3A%227d%22%7D&runtab=0
# https://python.langchain.com/docs/integrations/tools/sql_database/
# https://python.langchain.com/api_reference/community/tools/langchain_community.tools.sql_database.tool.QuerySQLCheckerTool.html

from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.messages import AIMessage
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_core.runnables import RunnablePassthrough, Runnable
from langchain_google_vertexai import VertexAIEmbeddings
# can be used instead of FAISS.


# Using this tutorial, https://blog.futuresmart.ai/mastering-natural-language-to-sql-with-langchain-nl2sql
# But will make a more complex model later, using OpenAI and then Ollama model next for the agent.
# create_sql_query_chain is just a PromptTemplate made by Langchain, we can make our own, which also includes examples...

# Need to convert chain into a tool for the agent to use it.
# https://python.langchain.com/docs/how_to/tools_chain/




import os
from dotenv import load_dotenv
from langchain_community.tools import QuerySQLDataBaseTool
from langchain_core.language_models import BaseChatModel, BaseLLM
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_ollama import OllamaLLM

from proj.chain.prompts_examples import examples

# Not needed but boilerplate for SQL prompting.
# from langchain.chains import create_sql_query_chain
# from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
import logging

from utils import get_credentials_path

# Set up logging configuration (place this at the top of your file)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Load the environmental variables into the system.
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = get_credentials_path()

# Database Connection Constant

# {os.getenv('DB_PASSWORD')}
db_connection_string = f"mysql://{os.getenv('DB_USER')}:@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
print("Connection String: ", db_connection_string)
db = SQLDatabase.from_uri(db_connection_string, )  # include_tables=["products"]


# Lambda Functions
def generate_better_sql_query_chain(prompt: str, llm: BaseChatModel | BaseLLM) -> str:
	# Converting this to dynamic few-shot example, for better performance.
	top_k = 3
	example_selector = SemanticSimilarityExampleSelector.from_examples(
		examples,
		# embeddings callable,
		VertexAIEmbeddings(model_name="text-embedding-004"),  # text-embedding-005
		FAISS,  # VertexAIVectorSearch
		k=top_k,
		input_keys=["input"]
	)

	example_prompt = PromptTemplate.from_template("User input: {input}\nSQL query: {query}")

	sql_prompt = FewShotPromptTemplate(
		example_selector=example_selector,
		example_prompt=example_prompt,
		input_variables=['input', 'table_info'],
		prefix=
		'You are a MySQL expert. Given an input question, first create a syntactically correct MySQL query to '
		'run, then look at the results of the query and return the answer to the input question.'
		'Unless the user specifies in the question a specific number of examples to obtain, query for at most '
		+ str(top_k) + ' results using the LIMIT clause as per MySQL. You can order the results to return the most '
		               'informative data in the database.'
		               'Never query for all columns from a table. You must query only the columns that are needed to answer '
		               'the question. Wrap each column name in backticks (`) to denote them as delimited identifiers.'
		               'Pay attention to use only the column names you can see in the tables below. Be careful to not query '
		               'for columns that do not exist. Also, pay attention to which column is in which table.'
		               'Pay attention to use CURDATE() function to get the current date, if the question involves "today".'
		               'Please note expiry information and orders will require queries that involve relations like JOIN between ids,'
		               ' please review column names carefully.'
		               ''
		               'Use the following format:'
		               ''
		               'Question: Question here'
		               'SQLQuery: SQL Query to run'
		               'SQLResult: Result of the SQLQuery'
		               'Answer: Final answer here'
		               ''
		               'Only use the following tables:'
		               '{table_info}'
		               ''
		               'Question: {input}'
		               'Please only respond with the SQL query.'
		               ''
		               ''
		               'Below are a number of examples of questions and their corresponding SQL queries.',
		suffix="User input: {input}\nSQL query: ",
	)
	# print("Prompt Used: ", sql_prompt)
	# Add custom instructions to llm model.
	chain = sql_prompt | llm
	# Execute the chain with the query.
	query = chain.invoke({"input": prompt, "table_info": db.get_table_info()})
	if isinstance(query, AIMessage):
		response = query.content
	else:
		response = query

	if any(keyword in response.upper() for keyword in ["DROP TABLE", "ALTER TABLE"]):
		raise "Action not allowed."
	return response.strip('`').replace('sql', '').replace('```', '').replace("\n", " ").replace("SQL:", "").replace("SQL", "").strip()


def execute_sql_query(query: str) -> str:
	execute_query = QuerySQLDataBaseTool(db=db)
	return execute_query.invoke(query)


def rephrase_db_results(llm: BaseChatModel | BaseLLM):
	answer_prompt = PromptTemplate.from_template(
	"""
	Given the following user question, corresponding SQL query, and SQL result, answer the user question.
	Please provide a concise answer, and ensure to only answer the user question provided.
	If a list is returned, please make sure to also mentions these items up to an extend (max 5), not ignore them.
	Please do not provide the schema or any other internal information not requested.

	Question: {question}
	SQL Query: {query}
	SQL Result: {result}
	Answer: 
	"""
	)
	rephrase_chain = answer_prompt | llm | StrOutputParser()
	# chain = (
	# 		{"question": RunnablePassthrough(), "query": RunnablePassthrough(), "result": RunnablePassthrough()}
	# 		| rephrase_answer
	# )
	# # return chain
	# return chain.invoke({"question": question, "query": query, "result": result})
	return rephrase_chain


def get_database_chain(llm: BaseChatModel | BaseLLM) -> Runnable:
    # Get the rephrase chain
    rephrase_chain = rephrase_db_results(llm)

    # Create functions that include logging
    def log_and_generate_sql(x):
        query = generate_better_sql_query_chain(x["question"], llm)
        logger.info(f"Generated SQL Query: {query}")
        return query

    def log_and_execute_sql(x):
        result = execute_sql_query(x["query"])
        logger.info(f"SQL Execution Result: {result}")
        return result

    def log_and_rephrase(x):
        output = rephrase_chain.invoke({
            "question": x["question"],
            "query": x["query"],
            "result": x["result"]
        })
        logger.info(f"Rephrased Output: {output}")
        return output

    # Create the master chain using proper RunnablePassthrough
    master_chain = (
        # Step 1: Generate SQL query
        {
            "question": RunnablePassthrough(),
            "query": log_and_generate_sql
        }
        | RunnablePassthrough.assign(
            # Step 2: Execute SQL query
            result=log_and_execute_sql
        )
        | RunnablePassthrough.assign(
            # Step 3: Rephrase results
            output=log_and_rephrase
        )
        | (lambda x: x["output"])  # Extract just the output string
    )

    return master_chain



if __name__ == "__main__":
	gm_llm = OllamaLLM(
		# model="gemma2-ft9",
		model="gemma2-ft2-structured",  # https://huggingface.co/bastienp/Gemma-2-2B-Instruct-structured-output
		temperature=0,
	)
	selected_llm = gm_llm
	chain = get_database_chain(llm=selected_llm)
	prompt = "give me the products that are expiring soonest"
	response = chain.invoke({"question": prompt})
	print("Response: ", response)

