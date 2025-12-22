from pathlib import Path
from urllib.parse import urlparse
from pypdf import PdfReader
from docx import Document
import textract
from consts import MODEL_NAME
from extracting_data.extracting_consts import JOB_DESCRIPTION, INPUT_ATTEMPTS
from extracting_data.extracting_prompts import EXTRACTION_PROMPT
import requests
from bs4 import BeautifulSoup
import os
from langchain_openai import ChatOpenAI


def extract_text_from_url(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        text = soup.get_text(separator=" ")
        text = " ".join(text.split())

        return text
    except Exception as e:
        print(f"Failed to reach link {url}:", e)


def read_pdf(path: str) -> str:
    reader = PdfReader(path)
    text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)
    return "\n".join(text)


def read_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)


def read_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def read_doc(path: str) -> str:
    text = textract.process(path)
    return text.decode("utf-8", errors="ignore")


def is_url_string(s):
    try:
        result = urlparse(s)
        return all([result.scheme, result.netloc])
    except:
        return None


def is_path_string(s):
    try:
        p = Path(s)
        return p.is_file()
    except:
        return None


class ReadDocuments:
    def __init__(
        self,
        doc_input=None,
        document_topic=JOB_DESCRIPTION,
        llm=None,
        init_pipeline=True,
    ):
        self.document_topic = document_topic
        self.llm = llm
        self.full_desciption_text = None
        self.doc_input = doc_input
        if init_pipeline:
            self.pipeline()

    def init_llm(self):
        self.llm = ChatOpenAI(
            model=MODEL_NAME,
            temperature=0,
            api_key=os.environ["NEBIUS_API_KEY"],
            base_url=os.environ["NEBIUS_BASE_URL"],
        )

    def init_doc_input(self):
        self.doc_input = input(
            f"Please enter {self.document_topic} data or provide path to file containing it\n"
        )

    def extract_text_per_local_document_type(self):
        if self.doc_input.endswith(".pdf"):
            reading_func = read_pdf
        elif self.doc_input.endswith(".docx"):
            reading_func = read_docx
        elif self.doc_input.endswith(".docx"):
            reading_func = read_doc
        elif self.doc_input.endswith(".txt"):
            reading_func = read_txt
        try:
            return reading_func(self.doc_input)
        except:
            self.doc_input = None
            print(f"Failed to read local document {self.doc_input}. Please resubmit ")

    def extract_text(self):
        path_str = is_path_string(self.doc_input)
        if path_str:
            return self.extract_text_per_local_document_type()
        elif is_url_string(self.doc_input):
            return extract_text_from_url(self.doc_input)
        else:
            return self.doc_input

    def pipeline(self):
        attmepts_count = 0
        while self.full_desciption_text is None and attmepts_count <= INPUT_ATTEMPTS:
            if self.doc_input is None:
                self.init_doc_input()
            self.full_desciption_text = self.extract_text()
            attmepts_count += 1
        if self.full_desciption_text is not None:
            if self.llm is None:
                self.init_llm()
            result = self.llm.invoke(
                EXTRACTION_PROMPT.format(
                    topic=self.document_topic, text=self.full_desciption_text
                )
            )
            self.full_desciption_text = result.content
        else:
            print(
                f"Failed to get the text for {self.document_topic}. See you next time"
            )
