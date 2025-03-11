import streamlit as st  
from PyPDF2 import PdfReader  
import pandas as pd  
from pptx import Presentation  
from docx import Document  
import requests  
from bs4 import BeautifulSoup  
import os  
from langchain.text_splitter import RecursiveCharacterTextSplitter  
from langchain_google_genai import GoogleGenerativeAIEmbeddings  
import google.generativeai as genai  
from langchain_community.vectorstores import FAISS  
from langchain_google_genai import ChatGoogleGenerativeAI  
from langchain.prompts import PromptTemplate  
from langchain.chains import RetrievalQA  
from dotenv import load_dotenv  
from pytube import YouTube  
from youtube_transcript_api import YouTubeTranscriptApi  
import time  

# Load environment variables  
load_dotenv('api.env')  

# Configure Google GenAI  
api_key = os.getenv("GOOGLE_API_KEY")  
if not api_key:  
    st.error("Google API Key is not configured! Please check your .env file.")  
    st.stop()  
genai.configure(api_key=api_key)  

# Define functions to extract text from different file types  
def get_pdf_text(pdf_docs):  
    text = ""  
    for pdf in pdf_docs:  
        pdf_reader = PdfReader(pdf)  
        for page in pdf_reader.pages:  
            text += page.extract_text()  
    return text  

def get_csv_text(csv_docs):  
    text = ""  
    for csv_file in csv_docs:  
        df = pd.read_csv(csv_file)  
        text += df.to_string(index=False)  
    return text  

def get_excel_text(excel_docs):  
    text = ""  
    for excel_file in excel_docs:  
        df = pd.read_excel(excel_file)  
        text += df.to_string(index=False)  
    return text  

def get_ppt_text(ppt_docs):  
    text = ""  
    for ppt in ppt_docs:  
        presentation = Presentation(ppt)  
        for slide in presentation.slides:  
            for shape in slide.shapes:  
                if hasattr(shape, "text"):  
                    text += shape.text + "\n"  
    return text  

def get_doc_text(doc_docs):  
    text = ""  
    for doc in doc_docs:  
        document = Document(doc)  
        for para in document.paragraphs:  
            text += para.text + "\n"  
    return text  

def get_txt_text(txt_docs):  
    text = ""  
    for txt_file in txt_docs:  
        text += txt_file.read().decode("utf-8") + "\n"  
    return text  

def get_website_text(url):  
    response = requests.get(url)  
    soup = BeautifulSoup(response.text, 'html.parser')  
    return soup.title.string  # Return the title of the webpage  

def get_youtube_details_and_transcript(video_url):  
    yt = YouTube(video_url)  
    title = yt.title  
    channel = yt.author  
    thumbnail_url = yt.thumbnail_url  
    video_id = yt.video_id  

    # Get transcript  
    try:  
        transcript = YouTubeTranscriptApi.get_transcript(video_id)  
        transcript_text = ' '.join([entry['text'] for entry in transcript])  
    except Exception as e:  
        transcript_text = f"Could not retrieve transcript: {e}"  

    return {  
        "title": title,  
        "channel": channel,  
        "thumbnail_url": thumbnail_url,  
        "transcript": transcript_text  
    }  

def get_text_chunks(text):  
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)  
    chunks = text_splitter.split_text(text)  
    return chunks  

def get_vector_store(text_chunks):  
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")  
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)  
    vector_store.save_local("faiss_index")  

def get_conversational_chain(retriever):  
    prompt_template = """Answer the question as detailed as possible from the provided context.  
Make sure to provide all the details.  
If the answer is not in the provided context, just say, "Answer is not available in the context."  
Do not provide a wrong answer.  

Context:  
{context}  

Question:  
{question}  

Answer:  
"""  
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])  
    model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.3)  

    chain = RetrievalQA.from_chain_type(  
        llm=model,  
        retriever=retriever,  
        chain_type="stuff",   
        chain_type_kwargs={"prompt": prompt},  
    )  
    return chain  

# Maintain chat history  
chat_history = []  

def user_input(user_question):  
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")  
    try:  
        # Load the vector store  
        new_db = FAISS.load_local("faiss_index", embeddings)  
        retriever = new_db.as_retriever()  

        # Initialize the conversational chain  
        chain = get_conversational_chain(retriever)  

        # Special responses  
        if "who are you" in user_question.lower() or "what is your purpose" in user_question.lower():  
            response = "I am Aura, your personal assistant. I can summarize files in over 40 languages and help you understand your documents better. Feel free to ask me anything!"  
            chat_history.append({"assistant": response})  
            return  

        # Retry logic  
        for attempt in range(5):  # Retry up to 5 times  
            try:  
                response = chain.invoke({"query": user_question})  
                chat_history.append({"assistant": response['result']})  
                break  
            except Exception as e:  
                if "ResourceExhausted" in str(e):  
                    wait_time = 2 ** attempt  # Exponential backoff  
                    st.warning(f"Quota exceeded, retrying in {wait_time} seconds...")  
                    time.sleep(wait_time)  
                else:  
                    st.error(f"An error occurred: {e}")  
                    break  
    except Exception as e:  
        st.error(f"An error occurred: {e}")  

def display_chat():  
    for chat in chat_history:  
        st.write(f"🤖 **Aura:** {chat['assistant']}")  
        st.markdown("---")  # Separator for chat messages  

def main():  
    st.set_page_config(page_title="A MultiLingual Summarizer for Enhanced Text Comprehension", layout="wide")  
    
    st.title("Aura - Your Summarizer Assistant")  
    st.write("Summarize and understand your documents better. Ask me anything!")  

    user_question = st.text_input("What do you want to know?", placeholder="Type your question here...")  

    if st.button("Submit"):  
        user_input(user_question)  

    st.subheader("Chat History")  
    display_chat()  # Ensure there's no colon here  

    # Sidebar for file uploads  
    with st.sidebar:  
        st.title("Upload Your Files")  
        
        file_type = st.selectbox("Select File Type", ["PDF", "CSV", "Excel", "PPT", "DOC", "TXT", "YouTube Video", "Website"])  
        
        if file_type == "PDF":  
            pdf_docs = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)  
        elif file_type == "CSV":  
            csv_docs = st.file_uploader("Upload CSVs", type=["csv"], accept_multiple_files=True)  
        elif file_type == "Excel":  
            excel_docs = st.file_uploader("Upload Excel Files", type=["xlsx"], accept_multiple_files=True)  
        elif file_type == "PPT":  
            ppt_docs = st.file_uploader("Upload PPTs", type=["pptx"], accept_multiple_files=True)  
        elif file_type == "DOC":  
            doc_docs = st.file_uploader("Upload DOCs", type=["docx"], accept_multiple_files=True)  
        elif file_type == "TXT":  
            txt_docs = st.file_uploader("Upload TXT Files", type=["txt"], accept_multiple_files=True)  
        elif file_type == "YouTube Video":  
            youtube_link = st.text_input("Enter YouTube Video Link")  
        else:  # Website  
            website_link = st.text_input("Enter Website URL")  
        
        if st.button("Submit & Process"):  
            with st.spinner("Processing..."):  
                try:  
                    raw_text = ""  

                    # Process based on file type selected  
                    if pdf_docs:  
                        raw_text += get_pdf_text(pdf_docs)  
                    elif csv_docs:  
                        raw_text += get_csv_text(csv_docs)  
                    elif excel_docs:  
                        raw_text += get_excel_text(excel_docs)  
                    elif ppt_docs:  
                        raw_text += get_ppt_text(ppt_docs)  
                    elif doc_docs:  
                        raw_text += get_doc_text(doc_docs)  
                    elif txt_docs:  
                        raw_text += get_txt_text(txt_docs)  
                    elif youtube_link:  
                        youtube_details = get_youtube_details_and_transcript(youtube_link)  
                        raw_text += youtube_details['transcript']  
                        st.image(youtube_details['thumbnail_url'], caption=f"{youtube_details['title']} by {youtube_details['channel']}")  
                    elif website_link:  
                        raw_text += get_website_text(website_link)  

                    text_chunks = get_text_chunks(raw_text)  
                    get_vector_store(text_chunks)  
                    st.success("Processing complete! You can now ask questions.")  
                except Exception as e:  
                    st.error(f"An error occurred while processing the files: {e}")  

if __name__ == "__main__":  
    main()