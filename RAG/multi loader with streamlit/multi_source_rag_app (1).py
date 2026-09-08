import os
import tempfile
import streamlit as st

# PDF loader
from langchain_community.document_loaders import PyPDFLoader

# Website loader
from langchain_community.document_loaders import WebBaseLoader

# YouTube transcript loader
from langchain_community.document_loaders import YoutubeLoader

# Split documents into smaller chunks
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Convert text into vectors
from langchain_huggingface import HuggingFaceEmbeddings

# Vector database
from langchain_community.vectorstores import FAISS

# LLM
from langchain_groq import ChatGroq

# Prompt + RAG chain utilities
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(page_title="Multi Source RAG Chatbot", page_icon="🤖", layout="wide")

ADMIN_PHONE = "9898 57 68 77"


# Streamlit reruns the Python script whenever the user interacts
# with the UI. Session state lets us keep our vector database
# and chat history between those reruns.
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "source_name" not in st.session_state:
    st.session_state.source_name = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# PAGE HEADER
# ============================================================

st.title("🤖 Multi-Source RAG Chatbot")

st.write(
    "Load information from a PDF, website, or YouTube transcript "
    "and ask questions using RAG."
)

st.markdown("""
    **RAG workflow**

    Source → Loader → Chunks → Embeddings → FAISS →
    Retriever → Context + Question → Prompt → LLM → Answer
    """)


# ============================================================
# EMBEDDING MODEL
# ============================================================


@st.cache_resource
def get_embeddings():
    # This model converts text into numerical vectors.
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


embeddings = get_embeddings()


# ============================================================
# GROQ LLM
# ============================================================
# ============================================================
# GROQ LLM
# ============================================================

# Put your Groq API key here.
GROQ_API_KEY = "your_api_key_here"
# Put the key into the environment.
# os.getenv("GROQ_API_KEY") will now be able to find it.
os.environ["GROQ_API_KEY"] = GROQ_API_KEY


@st.cache_resource
def get_llm():

    # Check whether the API key exists.
    if not os.getenv("GROQ_API_KEY"):
        return None

    # Create the Groq LLM.
    return ChatGroq(
        model="openai/gpt-oss-120b", temperature=0.2, api_key=os.getenv("GROQ_API_KEY")
    )


llm = get_llm()


# ============================================================
# DOCUMENT FORMATTER
# ============================================================


def format_docs(docs):
    """
    Convert retrieved LangChain Documents into one string.

    This string becomes the CONTEXT that we send to the LLM.
    """

    result = []

    for doc in docs:

        page = doc.metadata.get("page")

        if page is not None:
            source = f"PDF Page {page + 1}"
        else:
            source = doc.metadata.get("source", "Source")

        result.append(f"[{source}]\n{doc.page_content}")

    return "\n\n".join(result)


# ============================================================
# RAG PROMPT
# ============================================================


def get_prompt():
    """
    The prompt combines:

        retrieved context + user question

    The LLM is told not to invent information.
    """

    return ChatPromptTemplate.from_template(f"""
You are a helpful AI assistant.

Answer the user's question using ONLY the retrieved context.

Retrieved Context:
{{context}}

User Question:
{{question}}

Rules:
1. Use only the retrieved context.
2. Do not invent information.
3. Do not use outside knowledge if the answer is not in the context.
4. Answer clearly when the context supports the answer.
5. If the context does not contain enough information, do not guess.
6. If information is insufficient, say:

"I don't have enough information in the provided source to answer
this question. Please contact the administration at {ADMIN_PHONE}."

7. Never claim that you contacted the administration.

Answer:
""")


# ============================================================
# PDF LOADER
# ============================================================


def load_pdf(uploaded_file):
    """
    Save the Streamlit uploaded file temporarily because
    PyPDFLoader expects a file path.
    """

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:

        temp.write(uploaded_file.getbuffer())
        temp_path = temp.name

    try:
        loader = PyPDFLoader(temp_path)

        # Returns one Document object per PDF page.
        return loader.load()

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ============================================================
# WEB LOADER
# ============================================================


def load_web(url):
    """
    Download and extract readable content from a web page.
    """

    loader = WebBaseLoader(url)

    return loader.load()


# ============================================================
# YOUTUBE LOADER
# ============================================================


def load_youtube(url):
    """
    Load the transcript associated with a YouTube video.

    The video needs to have an accessible transcript/captions.
    """

    loader = YoutubeLoader.from_youtube_url(url, add_video_info=False)

    return loader.load()


# ============================================================
# CHUNKING
# ============================================================


def split_documents(documents):
    """
    Break large documents into smaller chunks.

    chunk_size controls chunk length.
    chunk_overlap keeps some text from the previous chunk
    so that context is not lost at chunk boundaries.
    """

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    return splitter.split_documents(documents)


# ============================================================
# VECTOR STORE
# ============================================================


def create_vector_store(chunks):
    """
    Convert chunks into embeddings and store them in FAISS.
    """

    return FAISS.from_documents(chunks, embeddings)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("📚 Choose Knowledge Source")

source_type = st.sidebar.radio(
    "Select a loader:", ["📄 PDF Loader", "🌐 Web Loader", "▶️ YouTube Loader"]
)

documents = None


# ============================================================
# PDF OPTION
# ============================================================

if source_type == "📄 PDF Loader":

    st.sidebar.subheader("Upload PDF")

    uploaded_file = st.sidebar.file_uploader("Choose a PDF", type=["pdf"])

    if uploaded_file:

        if st.sidebar.button("📥 Load PDF", use_container_width=True):

            with st.spinner("Loading PDF..."):

                try:
                    documents = load_pdf(uploaded_file)

                    st.session_state.source_name = uploaded_file.name

                    st.session_state.loaded_documents = documents

                except Exception as error:
                    st.sidebar.error(f"PDF loading failed: {error}")


# ============================================================
# WEB OPTION
# ============================================================

elif source_type == "🌐 Web Loader":

    st.sidebar.subheader("Website URL")

    url = st.sidebar.text_input("Enter website URL", placeholder="https://example.com")

    if st.sidebar.button("🌐 Load Website", use_container_width=True):

        if not url.strip():

            st.sidebar.warning("Please enter a URL.")

        else:

            with st.spinner("Loading website..."):

                try:
                    documents = load_web(url)

                    st.session_state.source_name = url
                    st.session_state.loaded_documents = documents

                except Exception as error:
                    st.sidebar.error(f"Website loading failed: {error}")


# ============================================================
# YOUTUBE OPTION
# ============================================================

elif source_type == "▶️ YouTube Loader":

    st.sidebar.subheader("YouTube URL")

    youtube_url = st.sidebar.text_input(
        "Enter YouTube URL", placeholder="https://www.youtube.com/watch?v=..."
    )

    if st.sidebar.button("▶️ Load YouTube Video", use_container_width=True):

        if not youtube_url.strip():

            st.sidebar.warning("Please enter a YouTube URL.")

        else:

            with st.spinner("Loading YouTube transcript..."):

                try:
                    documents = load_youtube(youtube_url)

                    st.session_state.source_name = youtube_url
                    st.session_state.loaded_documents = documents

                except Exception as error:
                    st.sidebar.error(f"YouTube loading failed: {error}")


# ============================================================
# BUILD KNOWLEDGE BASE
# ============================================================

if documents is not None:

    with st.spinner("Splitting documents and creating embeddings..."):

        try:

            # Step 1: Split source into chunks.
            chunks = split_documents(documents)

            # Step 2: Create FAISS vector store.
            st.session_state.vector_store = create_vector_store(chunks)

            # New source means new conversation.
            st.session_state.messages = []

            st.success(f"Knowledge base ready — {len(chunks)} chunks created.")

        except Exception as error:

            st.error(f"Could not create vector store: {error}")


# ============================================================
# CURRENT SOURCE
# ============================================================

if st.session_state.vector_store is not None:

    st.info(f"📚 Knowledge source: " f"{st.session_state.source_name}")


# ============================================================
# API KEY CHECK
# ============================================================

if llm is None:

    st.warning(
        "GROQ_API_KEY is not configured. "
        "Set it in your environment and restart Streamlit."
    )


# ============================================================
# SHOW OLD CHAT MESSAGES
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input("Ask a question about your selected source...")


# ============================================================
# RAG QUESTION ANSWERING
# ============================================================

if question:

    if st.session_state.vector_store is None:

        st.warning("First select a loader and load a source.")

        st.stop()

    if llm is None:

        st.error("Groq API key is missing.")

        st.stop()

    # Show and save user message.
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):

        with st.spinner("Searching and generating answer..."):

            try:

                # ----------------------------------------------
                # STEP 1: Create retriever
                # ----------------------------------------------

                retriever = st.session_state.vector_store.as_retriever(
                    search_kwargs={"k": 4}
                )

                # ----------------------------------------------
                # STEP 2: Retrieve relevant chunks
                #
                # This is the R in RAG.
                # ----------------------------------------------

                retrieved_docs = retriever.invoke(question)

                # ----------------------------------------------
                # STEP 3: Build RAG chain
                # ----------------------------------------------

                rag_chain = (
                    {
                        "context": retriever | format_docs,
                        "question": RunnablePassthrough(),
                    }
                    | get_prompt()
                    | llm
                    | StrOutputParser()
                )

                # ----------------------------------------------
                # STEP 4: Send context + question to LLM
                # ----------------------------------------------

                answer = rag_chain.invoke(question)

                # ----------------------------------------------
                # STEP 5: Display answer
                # ----------------------------------------------

                st.markdown(answer)

                # ----------------------------------------------
                # DEBUG / TEACHING VIEW
                #
                # Students can expand this section to see
                # exactly what the retriever found.
                # ----------------------------------------------

                with st.expander("🔍 Show retrieved context"):

                    st.write(
                        "These are the chunks retrieved before "
                        "the LLM generated the answer:"
                    )

                    for index, doc in enumerate(retrieved_docs, start=1):

                        page = doc.metadata.get("page")

                        if page is not None:
                            source = f"PDF Page {page + 1}"
                        else:
                            source = doc.metadata.get("source", "Source")

                        st.markdown(f"**Chunk {index} — {source}**")

                        st.write(doc.page_content)

                        st.divider()

                # Save assistant response.
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )

            except Exception as error:

                message = f"Error: {error}"

                st.error(message)

                st.session_state.messages.append(
                    {"role": "assistant", "content": message}
                )


# ============================================================
# CLEAR BUTTON
# ============================================================

st.sidebar.divider()

if st.sidebar.button("🗑️ Clear Knowledge Base & Chat", use_container_width=True):

    st.session_state.vector_store = None
    st.session_state.source_name = None
    st.session_state.messages = []

    st.rerun()
