import streamlit as st
import logging
from agents.agent_manager import group_chat
from agents.conversation_workflow import conversation_workflow
import asyncio
import threading
from docx import Document
import io

# Initialize logging
logging.basicConfig(level=logging.INFO)


# Function to check allowed file extensions
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"txt", "pdf", "docx"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Function to read file contents
def read_file_contents(file):
    filename = file.name.lower()
    try:
        if filename.endswith(".txt"):
            content = file.read()
            return content.decode("utf-8") if isinstance(content, bytes) else content
        elif filename.endswith(".pdf"):
            return extract_text_from_pdf(file)
        elif filename.endswith(".docx"):
            return extract_text_from_docx(file)
        else:
            return None
    except Exception as e:
        st.error(f"Error reading {filename}: {e}")
        return None


# Function to extract text from PDF files
def extract_text_from_pdf(file):
    import PyPDF2

    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None


# Function to extract text from DOCX files
def extract_text_from_docx(file):
    from docx import Document
    from io import BytesIO

    try:
        file.seek(0)
        document = Document(BytesIO(file.read()))
        text = "\n".join([para.text for para in document.paragraphs])
        return text
    except Exception as e:
        st.error(f"Error extracting text from DOCX: {e}")
        return None


# Function to run the workflow synchronously
def run_workflow(group_chat, text_input):
    # Run the conversation workflow
    try:
        with st.spinner("Processing..."):
            result = asyncio.run(conversation_workflow(group_chat))
        return result
    except Exception as e:
        st.error(f"An error occurred during processing: {e}")
        logging.error(f"Error during workflow: {e}")
        return None


def get_user_input():
    text_input = input("Enter text here: ")
    return text_input


def create_word_file(content):
    document = Document()
    document.add_paragraph(content)
    return document


def main():
    st.title("Warning Letter Processor")
    st.write("Please upload the warning letter and the template files.")

    # Initialize session state variables
    if "stage" not in st.session_state:
        st.session_state.stage = "upload"
    if "warning_letter_content" not in st.session_state:
        st.session_state.warning_letter_content = None
    if "template_content" not in st.session_state:
        st.session_state.template_content = None

    # Stage: Upload
    if st.session_state.stage == "upload":
        warning_letter_file = st.file_uploader(
            "Upload Warning Letter", type=["txt", "pdf", "docx"], key="warning_letter"
        )
        template_file = st.file_uploader(
            "Upload Template", type=["txt", "pdf", "docx"], key="template"
        )

        if warning_letter_file and template_file:
            # Validate and read files
            if not allowed_file(warning_letter_file.name):
                st.error(
                    "Invalid warning letter file type. Only TXT, PDF, and DOCX files are allowed."
                )
                return
            if not allowed_file(template_file.name):
                st.error(
                    "Invalid template file type. Only TXT, PDF, and DOCX files are allowed."
                )
                return

            st.session_state.warning_letter_content = read_file_contents(
                warning_letter_file
            )
            st.session_state.template_content = read_file_contents(template_file)

            if (
                st.session_state.warning_letter_content
                and st.session_state.template_content
            ):
                if st.button("Start Processing"):
                    # Set context for the group chat
                    group_chat.context = {
                        "warning_letter": st.session_state.warning_letter_content,
                        "template": st.session_state.template_content,
                    }

                    # Create a new thread to get user input
                    user_input_thread = threading.Thread(target=get_user_input)
                    user_input_thread.daemon = (
                        True  # Set as daemon so it exits when main thread exits
                    )
                    user_input_thread.start()

                    # Run the workflow synchronously and provide updates
                    result = run_workflow(group_chat, "")

                    if result:
                        st.success("Processing completed!")
                        approved_corrective_action_plan = group_chat.context.get(
                            "Approved_corrective_action_plan"
                        )
                        if approved_corrective_action_plan:
                            word_file = create_word_file(
                                approved_corrective_action_plan
                            )
                            with io.BytesIO() as output:
                                word_file.save(output)
                                data = output.getvalue()
                            st.download_button(
                                label="Download Approved Corrective Action Plan",
                                data=data,
                                file_name="approved_corrective_action_plan.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            )
                            st.write(approved_corrective_action_plan)
                    else:
                        st.error("An error occurred during processing.")


if __name__ == "__main__":
    main()
