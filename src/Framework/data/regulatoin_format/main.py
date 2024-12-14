import xml.etree.ElementTree as ET
import json

# Paths to the uploaded XML files
file_210_path = "/Users/mobin.azimipanah/Downloads/title-21-part 210 XML.xml"
file_211_path = "/Users/mobin.azimipanah/Downloads/title-21-part 211 XML.xml"


# Path to save the JSON file
output_path = "/Users/mobin.azimipanah/Desktop/Berkley/regulAItor/src/Framework/data/full_regulations1.json"

def parse_and_save_xml_to_json(file_paths, output_path):
    """
    Parse multiple XML files to extract sections and save them into a JSON structure.
    Each section will be stored as a key-value pair where the key is the citation (e.g., "21 CFR 210.1")
    and the value is the content of the section. The final JSON is saved to the specified output path.
    
    :param file_paths: List of paths to XML files to parse.
    :param output_path: Path to save the resulting JSON.
    """
    combined_sections = {}

    for file_path in file_paths:
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Find all sections (DIV8 elements)
        for div in root.findall(".//DIV8"):
            citation = div.attrib.get("N")
            if citation:
                # Extract the title (HEAD) and the body text (P)
                title = div.find("HEAD").text if div.find("HEAD") is not None else ""
                body = "\n".join(p.text for p in div.findall("P") if p.text)  # Concatenate all paragraph texts
                # Combine the title and body into the section content
                combined_sections[f"21 CFR {citation}"] = f"{title}\n{body}"

    # Save the combined sections to JSON
    with open(output_path, "w") as json_file:
        json.dump(combined_sections, json_file, indent=4)

    print(f"JSON file saved to: {output_path}")

# List of XML file paths to process
file_paths = [file_210_path, file_211_path]

# Parse the XML files and save the resulting JSON
parse_and_save_xml_to_json(file_paths, output_path)
