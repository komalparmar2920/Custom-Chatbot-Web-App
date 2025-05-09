from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import os
from groq import Groq
from dotenv import load_dotenv
import PyPDF2

load_dotenv(dotenv_path=".env", override=True)

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("Missing Groq API Key. Set it as an environment variable.")

try:
    groq_client = Groq(api_key=groq_api_key)
except Exception as e:
    print(f"❌ ERROR: Failed to initialize Groq client: {e}")
    exit(1)

scraped_content = ""
pdf_content = ""


def scrape_website(url):
    """Scrapes the entire website and extracts text."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        text = " ".join([p.text for p in soup.find_all("p")])
        return text[:4000] if text else "No readable text found."
    except requests.exceptions.RequestException as e:
        return f"Error scraping website: {str(e)}"


def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = []
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text.append(extracted)
            extracted_text = " ".join(text)
            return (
                extracted_text[:4000]
                if extracted_text
                else "No readable text found in the PDF."
            )

    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"


def chatbot_response(user_input, content):
    """Generates chatbot responses using LLaMA model via Groq API."""
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI chatbot answering questions based on given content.",
                },
                {
                    "role": "user",
                    "content": f"Content: {content}\nUser Question: {user_input}",
                },
            ],
            temperature=0.7,
            max_tokens=1024,
        )
        return (
            response.choices[0].message.content
            if response.choices
            else "No response from AI."
        )
    except Exception as e:
        return f"Error generating response: {str(e)}"


@app.route("/")
def home():
    """Renders the frontend."""
    return render_template("index.html")


@app.route("/scrape_website", methods=["POST"])
def scrape():
    """Handles website scraping."""
    global scraped_content, pdf_content
    pdf_content = ""
    data = request.json
    website_url = data.get("website_url", "").strip()

    if not website_url:
        return jsonify({"reply": "No URL provided."})

    scraped_content = scrape_website(website_url)
    return jsonify({"reply": "Website scraped successfully."})


@app.route("/chat", methods=["POST"])
def chat():
    """Handles chatbot interactions."""
    global scraped_content, pdf_content

    data = request.json
    user_input = data.get("message", "").strip()

    if not user_input:
        return jsonify({"reply": "Please enter a question."})

    if pdf_content:
        content = pdf_content
    elif scraped_content:
        content = scraped_content
    else:
        content = "No content available. please upload a PDF or enter a website URL"

    bot_reply = chatbot_response(user_input, content)
    return jsonify({"reply": bot_reply})


@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    global pdf_content

    if "file" not in request.files:
        return jsonify({"reply": "No file uploaded."})

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"reply": "No selected file."})

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    pdf_content = extract_text_from_pdf(file_path)
    return jsonify(
        {"reply": "PDF uploaded successfully. You can now ask questions based on it."}
    )


if __name__ == "__main__":
    app.run(debug=True)
