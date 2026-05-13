import os
import streamlit as st

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


@st.cache_resource
def load_llm():

    llm = ChatGroq(
        temperature=0,
        model_name="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY")
    )

    return llm