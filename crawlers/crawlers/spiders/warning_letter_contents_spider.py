"""
# Summary

Extract text content of an FDA warning letter from a web page.

This uses the JSON file with URLs dumped from the URL crawler, set via
env var: `URL_JSON`

# Running

Run this from the project root:

```bash
cd crawlers && URL_JSON=../warning_letter_links.json uv run scrapy crawl warning_letter_contents
```
"""

import json
import os
from pathlib import Path
from typing import override

from playwright.async_api import Page
from scrapy import Request, Spider

from ..items import WarningLetterItem

URL_JSON_ENV_VAR_KEY = "URL_JSON"


class WarningLetterContentsSpider(Spider):
    name = "warning_letter_contents"

    def start_requests(self):
        if URL_JSON_ENV_VAR_KEY not in os.environ:
            raise ValueError(
                f"User must supply the JSON file using the {URL_JSON_ENV_VAR_KEY} env var"
            )
        url_fp = os.environ[URL_JSON_ENV_VAR_KEY]

        with open(Path(url_fp)) as file:
            url_file = json.load(file)

        all_links = set()
        for page_data in url_file:
            for link in page_data["urls"]:
                all_links.add(link)

        all_links = list(all_links)

        for link in all_links:
            yield Request(link)

    @override
    def parse(self, response, **kwargs):
        # Create an item for each letter
        item = WarningLetterItem()

        # Use the URL to create a unique file name
        item["file_name"] = response.url.split("/")[-1]
        item["url"] = response.url

        # Extract the main content of the letter; adjust the selector as needed
        text = ""
        for text_chunk in response.xpath(
            '//*[@id="main-content"]/div[@role="main"]//text()'
        ).getall():
            text += text_chunk
        text = text.strip()
        item["content"] = text

        # Send the item to the pipeline for saving
        yield item
