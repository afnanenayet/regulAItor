# File: Framework/orchestrator.py

import requests

def process_warning_letter(warning_letter):
    url = 'http://localhost:8000/process_warning_letter'
    response = requests.post(url, json={'warning_letter': warning_letter})
    return response.json()

if __name__ == '__main__':
    # Example usage
    warning_letter_content = "Your FDA warning letter content here."
    result = process_warning_letter(warning_letter_content)
    print(result)