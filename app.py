import streamlit as st
from pathlib import Path
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain.agents import create_agent
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="LangChain: Chat with SQL DB", page_icon="🦜")
st.title("🦜 LangChain: Chat with SQL DB")
LOCALDB = "USE_LOCALDB"
MYSQL = "USE_SQL"

radio_opt = ["Use SQLLite 3 database", "Connect to your Database"]

selected_opt = st.sidebar.radio(label="Choose the DB which you wanna use" ,options = radio_opt)

if radio_opt.index(selected_opt) ==1:
    db_uri = MYSQL
    mysql_host = st.sidebar.text_input("Provide MySQL host")
    mysql_user = st.sidebar.text_input("MySQL User")
    mysql_password = st.sidebar.text_input("MYSQL PASSWORD", type="password")
    mysql_db = st.sidebar.text_input("MySQL database")
else:
    db_uri=LOCALDB

api_key = st.sidebar.text_input(label="Your API key", type="password")

if not db_uri:
    st.info("Please enter the db uri and other info")

if not api_key:
    st.info("Please enter your API key")

llm = ChatGroq(groq_api_key = api_key,model_name = "openai/gpt-oss-120b")

@st.cache_resource(ttl = "2h")
def configure_db(db_uri, mysql_host = None, mysql_user = None, mysql_password = None, mysql_db=None):
    if db_uri == LOCALDB:
        dbfilepath=(Path(__file__).parent/"student.db").absolute()
        #dbfilepath = (Path(__file__).parent"/student.db").absolute()
        #dbfilepath = (Path(__file__).parent"/student.db").absolute()
        print(dbfilepath)
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator = creator))
    elif db_uri==MYSQL:
        if not(mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide all mysql details")
            st.stop()
        return SQLDatabase(create_engine(f"mysql+connector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"))

if db_uri ==MYSQL:
    db = configure_db(db_uri, mysql_host, mysql_user, mysql_password, mysql_db)
else:
    db = configure_db(db_uri)


toolkit=SQLDatabaseToolkit(db=db,llm=llm)

agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    agent_type="tool-calling",
    verbose=True,
    agent_executor_kwargs={"handle_parsing_errors": True},
)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role":"assistant", "content":"how can i help you"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input(placeholder = "Ask anything from the database")

if user_query:
    st.session_state.messages.append({"role":"user", "content":user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container())
        response = agent.invoke(
        {"input": user_query},
        config={"callbacks": [st_cb]}
)
    st.session_state.messages.append({"role":"assistant","content":response["output"]})
    st.write(response["output"])

