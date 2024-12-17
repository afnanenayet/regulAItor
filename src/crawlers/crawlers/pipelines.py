from pathlib import Path


class WarningLetterTextPipeline:
    def process_item(self, item, spider):
        # Define the directory to store the files
        save_path = Path(spider.settings.get("FILES_STORE", "warning_letter_data"))

        # Ensure the directory exists
        save_path.mkdir(parents=True, exist_ok=True)

        # Define the file path and write the content to a file
        file_path = save_path / f"{item['file_name']}.txt"
        file_path.write_text(item["content"])
