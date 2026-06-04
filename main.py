from fastapi import FastAPI
from pydantic import BaseModel
import os
import json
import re
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_classic.memory import ConversationBufferMemory
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.prompts import PromptTemplate

def remove_emojis(text):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                      "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

working_dir = os.path.dirname(os.path.realpath(__file__))
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(working_dir, ".env"))
except ImportError:
    pass

config_path = f"{working_dir}/config.json"
GROQ_API_KEY = (
    os.environ.get("GROQ_API_KEY", "").strip()
    or os.environ.get("Api_key", "").strip()
)
if not GROQ_API_KEY and os.path.exists(config_path):
    config_data = json.load(open(config_path))
    GROQ_API_KEY = config_data.get("GROQ_API_KEY", "").strip()
if GROQ_API_KEY:
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# FastAPI app and Pydantic model for API input
app = FastAPI()

class MessageRequest(BaseModel):
    message: str

# FastAPI route for chatbot
@app.post("/chat")
async def chatbot(request: MessageRequest):
    message = request.message

    # Setup vectorstore (same as Streamlit code)
    vectorstore = setup_vectorstore()

    # Setup the conversational chain (same as Streamlit code)
    conversational_chain = chat_chain(vectorstore)

    # Check for sensitive topics
    if contains_sensitive_topics(message):
        response = "It seems you may be experiencing distress. Please know that help is available. If you feel unsafe or overwhelmed, consider calling emergency services immediately. For ongoing support, here are some mental health helpline numbers: [Provide relevant Indian mental health helpline numbers]. We strongly encourage you to seek professional help."
    else:
        # Get response from the conversational chain
        response = conversational_chain({"question": message})["answer"]

    return {"response": response}

# Default prompts
DEFAULT_SYSTEM_PROMPT = """You are a specialized mental health assistant focused exclusively on mental health topics. 
Your role is to provide support, information, and guidance about mental health while maintaining professional boundaries.
Always respond with care, compassion, and evidence-based information from the provided context. 
Keep the response concise and to the point and also short but not too short, short enough to be read in one go.
Also make use of bullet points and lists wherever necessary.
Make use of few emojis only to make the response somewhat engaging and interesting.

When you receive a query:
1. First check if the provided context contains relevant mental health information
2. If the context is empty or not relevant to mental health, politely inform the user that you can only discuss mental health topics
3. If the context contains relevant information, provide a helpful response based on that information
4. For every incoming query, first assess whether it includes any trigger words/phrases related to self-harm, suicide, or harmful behaviors
5. If trigger words/phrases are detected, append the following to your response:
   "It seems you may be experiencing distress. Please know that help is available. If you feel unsafe or overwhelmed, consider calling emergency services immediately. For ongoing support, here are some mental health helpline numbers: [Provide relevant Indian mental health helpline numbers]. We strongly encourage you to seek professional help."
6. If no trigger words/phrases are detected, respond normally without including the helpline information

Remember: 
- Only respond to questions where you can find relevant mental health information in the context
- Be empathetic and supportive in your responses
- Focus on providing evidence-based information from the context and the vector database
- When discussing sensitive topics, maintain a professional and caring tone
- Always encourage seeking professional help when appropriate and needed, and when use of words/phrases related to self-harm, suicide, harmful behaviors, etc. are detected"""

DEFAULT_NEGATIVE_PROMPT = """Do not provide medical diagnoses, prescribe medications, or give specific treatment recommendations.
Do not encourage harmful behaviors or provide potentially dangerous advice.
Do not claim to be a licensed therapist or medical professional.
Do not provide any response that is not based on the provided mental health context and/ or the vector database.
If the context doesn't contain relevant mental health information, acknowledge this and politely inform the user that you can only discuss mental health topics.
Do not make assumptions about the user's mental state or condition.
Do not provide generic advice without context.
Do not share personal opinions or anecdotes."""

def contains_sensitive_topics(question):
    sensitive_keywords = [
        'suicide', 'self-harm', 'self harm', 'kill myself', 'kill', 'end my life',
        'want to die', 'hurting myself', 'cutting', 'overdose', 'harm myself',
        'suicidal', 'self injury', 'self-injury', 'self mutilation',
        'self-mutilation', 'suicidal thoughts', 'suicidal ideation',
        'harmful behaviors', 'hurting myself', 'ending it all', 'no reason to live',
        'can\'t go on', 'want to disappear', 'don\'t want to exist'
    ]
    
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in sensitive_keywords)

def setup_vectorstore():
    persist_directory = f"{working_dir}/vector_db_dir"
    embeddings = HuggingFaceEmbeddings()
    vectorstore = Chroma(persist_directory=persist_directory,
                         embedding_function=embeddings)
    return vectorstore

def chat_chain(vectorstore, system_prompt=DEFAULT_SYSTEM_PROMPT, negative_prompt=DEFAULT_NEGATIVE_PROMPT):
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0
    )
    
    # Create a combined prompt template
    prompt_template = f"""{system_prompt}

{negative_prompt}

Context (from mental health database):
{{context}}

Chat History:
{{chat_history}}

Question: {{question}}

Answer:"""
    
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "chat_history", "question"]
    )
    
    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3}  # Retrieve top 3 most relevant documents
    )
    memory = ConversationBufferMemory(
        llm = llm,
        output_key = "answer",
        memory_key = "chat_history",
        return_messages = True
    )
    
    chain = ConversationalRetrievalChain.from_llm(
        llm = llm,
        retriever = retriever,
        chain_type = "stuff",
        memory = memory,
        verbose = True,
        return_source_documents = True,
        combine_docs_chain_kwargs={"prompt": prompt}
    )
    return chain
