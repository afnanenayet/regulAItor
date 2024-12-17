# File: /Framework/orchestrator.py

import requests

def process_warning_letter(warning_letter, template=""):
    url = 'http://localhost:8000/process_warning_letter'
    try:
        response = requests.post(url, json={'warning_letter': warning_letter, 'template': template})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error processing warning letter: {e}")
        return {"error": str(e)}

if __name__ == '__main__':
    # Example usage
    warning_letter_content = "Your FDA warning letter content here."
    template_content = "Your corrective action plan template here."
    result = process_warning_letter(warning_letter_content, template_content)
    print(result)