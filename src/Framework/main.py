# File: /Framework/main.py

from flask import Flask, request, jsonify, render_template
from agents.agent_manager import group_chat
from agents.conversation_workflow import conversation_workflow
import os
import asyncio  
import logging
from autogen import runtime_logging

log_file_path = "autogen_logs/runtime.log"
if os.path.exists(log_file_path):
    os.remove(log_file_path)
"""
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
"""
app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit files to 16 MB
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process_warning_letter', methods=['POST'])
def process_warning_letter():
    if 'warning_letter' not in request.files or 'template' not in request.files:
        return jsonify({"error": "Please upload both the warning letter and the template files."}), 400

    warning_letter_file = request.files['warning_letter']
    template_file = request.files['template']

    if not allowed_file(warning_letter_file.filename) or not allowed_file(template_file.filename):
        return jsonify({"error": "Invalid file type. Only TXT, PDF, and DOCX files are allowed."}), 400

    warning_letter_content = read_file_contents(warning_letter_file)
    template_content = read_file_contents(template_file)

    if not warning_letter_content or not template_content:
        return jsonify({"error": "Could not read the uploaded files."}), 400

    # Set context for the group chat
    group_chat.context = {
        "warning_letter": warning_letter_content,
        "template": template_content
    }
    #logging.debug(f"Group chat context set: {group_chat.context}")
    #logging.debug("Starting conversation workflow...")
    # Run the conversation workflow asynchronously

    logging_session_id = runtime_logging.start(logger_type="file", config={"filename": "runtime.log"})

    result = asyncio.run(conversation_workflow(group_chat))

        # Check if user input is required
    if result.get("user_input_required", False):
        error_message = "Validation failed. Please provide a valid FDA warning letter."
        return render_template('reupload.html', error_message=error_message)
    runtime_logging.stop()

    # Collect results from the corrective action plan
    corrective_action_plan = result.get("corrective_action_plan", "")

    return render_template('result.html', corrective_action_plan=corrective_action_plan)

def read_file_contents(file):
    filename = file.filename.lower()
    try:
        if filename.endswith('.txt'):
            return file.read().decode('utf-8')
        elif filename.endswith('.pdf'):
            return extract_text_from_pdf(file)
        elif filename.endswith('.docx'):
            return extract_text_from_docx(file)
        else:
            return None
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return None

def extract_text_from_pdf(file):
    import PyPDF2
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

def extract_text_from_docx(file):
    from docx import Document
    try:
        document = Document(file)
        text = '\n'.join([para.text for para in document.paragraphs])
        return text
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)