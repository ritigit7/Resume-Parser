import streamlit as st
import re
import os
import pandas as pd
from PyPDF2 import PdfReader
from docx import Document
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

template = """Extract all relevant details from the given resume text. 
Ensure that these details are correctly extracted.

### Resume Text:
{resume_text}

Focus on:
**Personal Information**  
- Full Name  
- Email  
- Phone Number  
- LinkedIn  
- GitHub/Portfolio  

**Professional Summary**  
- Brief Introduction  
- Total Experience  
- Current Job Title  
- Current Employer  
- Key Strengths  

**Work Experience**  
- Company Name  
- Job Title  
- Employment Duration  
- Location  
- Roles & Responsibilities  
- Key Achievements  

**Education**  
- Degree  
- Field of Study  
- University Name  
- Year of Passing  

**Skills**  
- Technical & Soft Skills  

**Projects**  
- Project Name  
- Description  
- Technologies Used  
- Role & Contribution  
- Outcome/Impact  

**Certifications & Awards**  
- Certifications & Achievements  

Return the extracted details in a well-formatted manner without using JSON.
The first part of the text always contains personal information such as Full Name, Email, Phone Number, LinkedIn, and GitHub/Portfolio."""

chat_prompt = ChatPromptTemplate.from_template(template)
# llm = OllamaLLM(model="mistral")
llm = OllamaLLM(model="llama3.2")
# llm = OllamaLLM(model="phi3:3.8b")
# llm = OllamaLLM(model="deepseek-r1:8b")
# llm = OllamaLLM(model="deepseek-r1:1.5b")
chain = chat_prompt | llm

st.set_page_config(page_title="Resume Parser", layout="wide")
st.sidebar.title("📄 Resume Parser App")
st.sidebar.write("Upload a resume in PDF or DOCX format to extract structured information.")

uploaded_file = st.sidebar.file_uploader("Upload Resume", type=["pdf", "docx"])

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return text

def extract_text_from_docx(file):
    doc = Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

if uploaded_file is not None:
    file_extension = uploaded_file.name.split(".")[-1].lower()
    
    if file_extension == "pdf":
        resume_text = extract_text_from_pdf(uploaded_file)
    elif file_extension == "docx":
        resume_text = extract_text_from_docx(uploaded_file)
    else:
        st.sidebar.error("Unsupported file format. Please upload a PDF or DOCX file.")
        st.stop()
    
    st.sidebar.subheader("Extracted Resume Text:")
    st.sidebar.text_area("Resume Content", resume_text, height=200)
    
    if st.sidebar.button("Parse Resume"):
        with st.spinner("Extracting details..."):
            response = chain.invoke({"resume_text": resume_text})
            # pattern = r'<think>(.*?)</think>'
            # match = re.search(pattern, response, re.DOTALL)
            # print(match.span())
            # structured_data = response[match.end()+1:]
            structured_data = response
        
        tabs = st.tabs(["Personal Info", "Professional Summary", "Experience", "Education", "Skills", "Projects", "Certifications & Awards"])
        
        with tabs[0]:
            st.subheader("📌 Personal Information")
            st.write(structured_data.split("**Professional Summary**")[0].strip())
        
        with tabs[1]:
            st.subheader("💼 Professional Summary")
            st.write(structured_data.split("**Work Experience**")[0].split("**Professional Summary**")[-1].strip())
        
        with tabs[2]:
            st.subheader("🏢 Work Experience")
            st.write(structured_data.split("**Education**")[0].split("**Work Experience**")[-1].strip())
        
        with tabs[3]:
            st.subheader("🎓 Education")
            st.write(structured_data.split("**Skills**")[0].split("**Education**")[-1].strip())
        
        with tabs[4]:
            st.subheader("🛠 Skills")
            st.write(structured_data.split("**Projects**")[0].split("**Skills**")[-1].strip())
        
        with tabs[5]:
            st.subheader("🚀 Projects")
            st.write(structured_data.split("**Certifications & Awards**")[0].split("**Projects**")[-1].strip())
        
        with tabs[6]:
            st.subheader("🏅 Certifications & Awards")
            st.write(structured_data.split("**Certifications & Awards**")[-1].strip())
