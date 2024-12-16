import streamlit as st
import os
import asyncio
import logging
import sys
from io import StringIO
from agents.agent_manager import group_chat
from agents.conversation_workflow import conversation_workflow
from autogen import runtime_logging


# Function to check allowed file extensions
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {"txt", "pdf", "docx"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Function to read file contents
def read_file_contents(file):
    filename = file.name.lower()
    try:
        if filename.endswith(".txt"):
            return file.read().decode("utf-8")
        elif filename.endswith(".pdf"):
            return extract_text_from_pdf(file)
        elif filename.endswith(".docx"):
            return extract_text_from_docx(file)
        else:
            return None
    except Exception as e:
        st.error(f"Error reading {filename}: {e}")
        return None


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


async def run_workflow(group_chat, output_placeholder, progress_bar):
    # Redirect stdout to capture the logs
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()

    # Run the conversation workflow asynchronously
    logging_session_id = runtime_logging.start(
        logger_type="file", config={"filename": "runtime.log"}
    )

    loop = asyncio.get_event_loop()

    # Start the conversation workflow
    task = loop.create_task(conversation_workflow(group_chat))

    # Run the event loop and update the output in real-time
    while not task.done():
        # Get the current output and display it
        output = mystdout.getvalue()
        output_placeholder.write(output)

        # Sleep briefly to avoid locking up the interface
        await asyncio.sleep(0.1)

    result = task.result()

    runtime_logging.stop()

    # Reset stdout
    sys.stdout = old_stdout

    # Display final output
    output = mystdout.getvalue()
    output_placeholder.write(output)
    progress_bar.progress(100)

    return result


def main():
    st.title("Warning Letter Processor")
    st.write("Please upload the warning letter and the template files.")

    # Initialize session state for controlling the workflow
    if "stage" not in st.session_state:
        st.session_state.stage = "upload"
    if "result" not in st.session_state:
        st.session_state.result = None

    if st.session_state.stage == "upload":
        warning_letter_file = st.file_uploader(
            "Warning Letter", type=["txt", "pdf", "docx"]
        )
        template_file = st.file_uploader("Template", type=["txt", "pdf", "docx"])

        if warning_letter_file and template_file:
            # Validate file types
            if not allowed_file(warning_letter_file.name) or not allowed_file(
                template_file.name
            ):
                st.error(
                    "Invalid file type. Only TXT, PDF, and DOCX files are allowed."
                )
                return

            warning_letter_content = read_file_contents(warning_letter_file)
            template_content = read_file_contents(template_file)

            if warning_letter_content and template_content:
                # Store contents in session state
                st.session_state.warning_letter_content = warning_letter_content
                st.session_state.template_content = template_content

                # Enable 'Start Processing' button
                if st.button("Start Processing"):
                    st.session_state.stage = "processing"
            else:
                st.error("Could not read the uploaded files.")
        else:
            st.info("Awaiting file uploads...")
    elif st.session_state.stage == "processing":
        # Set context for the group chat
        group_chat.context = {
            "warning_letter": st.session_state.warning_letter_content,
            "template": st.session_state.template_content,
        }

        # Prepare placeholders for real-time output
        output_placeholder = st.empty()
        progress_bar = st.progress(0)

        # Run the conversation workflow up to input validation
        async def run_to_validation():
            # Redirect stdout to capture the logs
            old_stdout = sys.stdout
            sys.stdout = mystdout = StringIO()

            # Run the conversation workflow asynchronously
            logging_session_id = runtime_logging.start(
                logger_type="file", config={"filename": "runtime.log"}
            )

            loop = asyncio.get_event_loop()

            # Start the conversation workflow
            task = loop.create_task(conversation_workflow(group_chat))

            # Run until input validation is done
            while not task.done():
                # Check if input validation agent has finished
                if group_chat.context.get("input_validation_result") is not None:
                    break

                # Get the current output and display it
                output = mystdout.getvalue()
                output_placeholder.write(output)

                # Sleep briefly
                await asyncio.sleep(0.1)

            # Capture the output up to this point
            output = mystdout.getvalue()
            output_placeholder.write(output)
            progress_bar.progress(50)

            runtime_logging.stop()

            # Reset stdout
            sys.stdout = old_stdout

            # Check validation result
            if group_chat.context.get("input_validation_result"):
                st.success("Input validation successful.")
            else:
                st.error(
                    "Validation failed. Please provide a valid FDA warning letter."
                )
                st.session_state.stage = "upload"
                return

            # Ask for confirmation to continue
            confirmation_button = st.button("Confirm to Continue Processing")
            if confirmation_button:
                st.session_state.stage = "continue_processing"

        asyncio.run(run_to_validation())

    elif st.session_state.stage == "continue_processing":
        # Continue processing
        group_chat.context["user_confirmed"] = True

        # Prepare placeholders for real-time output
        output_placeholder = st.empty()
        progress_bar = st.progress(50)

        # Run the rest of the conversation workflow
        asyncio.run(run_workflow(group_chat, output_placeholder, progress_bar))

        st.session_state.stage = "completed"
    elif st.session_state.stage == "completed":
        # Display the final results
        corrective_action_plan = group_chat.context.get("corrective_action_plan", "")
        st.success("Corrective Action Plan:")
        st.write(corrective_action_plan)


if __name__ == "__main__":
    main()
