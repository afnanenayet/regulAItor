# main.py

import asyncio
import logging
import json
from pathlib import Path
from config import ProcessorConfig
from processor import FDALetterProcessor

async def main():
    config = ProcessorConfig(
        input_dir=Path("warning_letter_data"),
        output_dir=Path("output"),
        max_validation_attempts=3,  # Maximum revision attempts
        max_turns=3  # Maximum number of conversation rounds
    )
    
    processor = FDALetterProcessor(config)
    
    try:
        logging.info("Starting FDA warning letter processing...")
        
        files = list(config.input_dir.glob("*.txt"))
        if not files:
            logging.warning("No files found in the input directory.")
            return
        
        summaries = []
        
        for file_path in files:
            logging.info(f"Processing file: {file_path}")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                letter_name = file_path.stem
                validated_summary = await processor.process_letter(letter_name, content)
                
                if validated_summary:
                    summaries.append(validated_summary)
                    logging.info(f"Successfully processed {letter_name}")
                else:
                    logging.warning(f"Failed to process {letter_name}")
            
            except Exception as e:
                logging.error(f"Error processing file {file_path}: {e}")
                continue
        
        # Ensure output directory exists
        config.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write summaries to file even if the list is empty
        output_file = config.output_dir / "validated_summaries.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summaries, f, indent=2, ensure_ascii=False)
        
        if summaries:
            logging.info(f"Successfully wrote {len(summaries)} summaries to {output_file}")
        else:
            logging.warning("Wrote empty summaries list to output file")
            
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        raise
    finally:
        await processor.cleanup()
        logging.info("Processing completed.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())