"""
A quick and dirty streamlit UI for generating FDA warning letter summaries.
"""

import streamlit as st

from config import ProcessorConfig
from processor import FDALetterProcessor
from pathlib import Path

st.title("Analyze FDA warning letter")

config = ProcessorConfig(
    input_dir=Path("warning_letter_data"),  # TODO: check this path
    output_dir=Path("output"),
    max_validation_attempts=3,  # Maximum revision attempts
    max_turns=3,  # Maximum number of conversation rounds
)

processor = FDALetterProcessor(config)

with st.form("input_form"):
    prompt_letter_id = st.text_input("Letter ID")
    prompt_contents = st.text_area("FDA warning letter contents")
    submit = st.form_submit_button("Analyze and summarize")

if submit:
    with st.status("Analyzing with the power of a million GPUs"):
        validated_summary = processor.process_letter(prompt_letter_id, prompt_contents)

    if validated_summary:
        st.write(f":white_check_mark: Successfully summarized {prompt_letter_id}")
        st.header("Summary")
        st.subheader("Violated terms")
        st.write("\n".join([f"- {x}" for x in validated_summary["violated_terms"]]))
        st.subheader("Recommendations")
        st.write("\n".join([f"- {x}" for x in validated_summary["recommendations"]]))

        with st.expander("See as JSON"):
            st.json(validated_summary)
    else:
        st.write(f":x: Failed to summarize {prompt_letter_id}")
