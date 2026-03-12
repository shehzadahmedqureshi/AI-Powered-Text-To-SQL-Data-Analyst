import json
import os
import re
import sqlite3

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel
from sqlalchemy import create_engine, inspect


load_dotenv()

db_url = "sqlite:///amazon.db"


def extract_schema(db_url: str) -> str:
    engine = create_engine(db_url)
    inspector = inspect(engine)
    schema: dict[str, list[str]] = {}

    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        schema[table_name] = [col["name"] for col in columns]
    return json.dumps(schema)


def text_to_sql(schema: str, prompt: str) -> str:
    system_prompt = """
    You are an expert SQL generator. Given a database schema and a user prompt, generate a valid SQL query that answers the prompt. 
    Only use the tables and columns provided in the schema. ALWAYS ensure the SQL syntax is correct and avoid using any unsupported features. 
    Output only the SQL as your response will be directly used to query data from the database. No preamble please.
    """

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", "Schema:\n{schema}\n\nQuestion: {user_prompt}\n\nSQL Query:"),
        ]
    )

    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise RuntimeError("GROQ_API_KEY is not set in the environment.")

    groq_model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    model = ChatGroq(
        model=groq_model,
        temperature=0,
        api_key=groq_api_key,
    )

    chain = prompt_template | model | StrOutputParser()

    raw_response = chain.invoke({"schema": schema, "user_prompt": prompt})
    cleaned_response = re.sub(r"<think>.*?</think>", "", raw_response, flags=re.DOTALL)
    return cleaned_response.strip()


def get_data_from_database(prompt: str):
    schema = extract_schema(db_url)
    sql_query = text_to_sql(schema, prompt)
    conn = sqlite3.connect("amazon.db")
    cursor = conn.cursor()
    res = cursor.execute(sql_query)
    results = res.fetchall()
    conn.close()
    return results


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    question: str


class AnalyzeResponse(BaseModel):
    results: list


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    results = get_data_from_database(request.question)
    return AnalyzeResponse(results=results)
