from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import streamlit as st
from langchain.chains import LLMChain
from dataclasses import dataclass
from langchain_core.output_parsers import StrOutputParser
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import LlamaCpp
import os

current_directory = os.path.dirname(os.path.abspath(__file__))
model_relative_path = "sqlcoder-7b-2-GGUF/sqlcoder-7b-2.Q8_0.gguf"
model_directory = os.path.join(current_directory, model_relative_path)
GOOGLE_API_KEY = "AIzaSyBseEjkWopXJgJZTJ_vG9xp4pkkJAqLwVE"
Palmllm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY)
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
n_gpu_layers = 5  # The number of layers to put on the GPU. The rest will be on the CPU. If you don't know how many layers there are, you can use -1 to move all to GPU.
n_batch = 400  # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.

# Make sure the model path is correct for your system!
def initialise_sqlcoder():
    global sql_llm
    
    sql_llm = LlamaCpp(
        model_path=model_directory,
        n_gpu_layers=n_gpu_layers,
        n_batch=n_batch,
        callback_manager=callback_manager,
         # Verbose is required to pass to the callback manager
    )

# Define the initial content of the prompt template input box
initial_template_content = """## Task
Generate a SQL query to answer the following question:
`{question}`

### Database Schema
This query will run on a database whose schema is represented in this string:
CREATE TABLE products (
  product_id INTEGER PRIMARY KEY, -- Unique ID for each product
  name VARCHAR(50), -- Name of the product
  price DECIMAL(10,2), -- Price of each unit of the product
  quantity INTEGER  -- Current quantity in stock
);

CREATE TABLE sales (
  sale_id INTEGER PRIMARY KEY, -- Unique ID for each sale
  product_id INTEGER, -- ID of product sold
  customer_id INTEGER,  -- ID of customer who made purchase
  salesperson_id INTEGER, -- ID of salesperson who made the sale
  sale_date DATE, -- Date the sale occurred
  quantity INTEGER -- Quantity of product sold
);

-- sales.product_id can be joined with products.product_id

### SQL
Given the database schema, here is the SQL query that answers `{question}`:
```sql
"""

# Create the prompt template input box with the initial content
template_input = st.sidebar.text_area("Enter Prompt Template", initial_template_content, height=460)
st.session_state["template_content"]=None
# Reset the content of the input box to the initial content whenever necessary
if st.session_state["template_content"]==None:
    st.session_state["template_content"] = template_input
else:
    template_input = st.session_state["template_content"]

prompt = PromptTemplate.from_template(template_input)

# Define the options for the dropdown box
model_options = ["Palm API", "SQLCoder 7b2"]
st.session_state["selected_tool"]=None
# Create the dropdown box with the initial content
selected_tool = st.sidebar.selectbox("Choose the Model", model_options)

# Reset the selected option to the initial content whenever necessary
if st.session_state["selected_tool"]==None:
    st.session_state["selected_tool"] = selected_tool
else:
    selected_tool = st.session_state["selected_tool"]

@dataclass
class Message:
    actor: str
    payload: str


USER = "user"
ASSISTANT = "ai"
MESSAGES = "messages"
if MESSAGES not in st.session_state:
    st.session_state[MESSAGES] = [Message(actor=ASSISTANT, payload="Hi! How can I help you?")]

msg: Message
for msg in st.session_state[MESSAGES]:
    st.chat_message(msg.actor).write(msg.payload)

question: str = st.chat_input("Enter a prompt here")

if question:
    st.session_state[MESSAGES].append(Message(actor=USER, payload=question))
    st.chat_message(USER).write(question)
    if st.session_state["selected_tool"] == "Palm API":
        print('palm')
        model = Palmllm
    else:
        initialise_sqlcoder()
        model=sql_llm
    chain = LLMChain(prompt=prompt, llm=model)
    response = chain.invoke(question)
    st.session_state[MESSAGES].append(Message(actor=ASSISTANT, payload=response))
    st.chat_message(ASSISTANT).write(response)
