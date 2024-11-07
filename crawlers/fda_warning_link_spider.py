"""
# Synopsis
Defines spiders to crawl for links to FDA warning letter URLs.

This is a bit more complicated than it seems because the tables are loaded dynamically on the page,
so we need to use playwright to dynamically update the page.

# Running

You need to run this via scrapy:

```bash
uv run scrapy runspider fda_warning_link_spider.py -o warning_letter_links.json
```

You can omit `uv run` if you're not using `uv`.
"""

from playwright.async_api import Page
from scrapy import Request, Spider


class WarningLetterUrlSpider(Spider):
    """Get the URLs to all of the warning letters."""

    name: str = "warning_letter_urls"

    custom_settings = {
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "DOWNLOAD_HANDLERS": {
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": True  # Set to False if you want to see the browser while debugging
        },
    }

    start_urls = [
        "https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/compliance-actions-and-activities/warning-letters"
    ]

    def start_requests(self):
        yield Request(
            self.start_urls[0],
            meta={
                "playwright": True,
                "playwright_include_page": True,
            },
        )

    async def parse(self, response, **kwargs):
        page: Page = response.meta["playwright_page"]
        page_counter = 0

        while True:
            # Extract all links in the table for the current page
            page_links = []
            links = await page.query_selector_all("table tbody tr a")
            for link in links:
                href = await link.get_attribute("href")
                text = await link.inner_text()
                if href:
                    page_links.append(response.urljoin(href))

            if page_links:
                yield {
                    "urls": page_links,
                    "page_number": page_counter,
                }

            # Locate the "Next" button and break if it's not found or not clickable
            next_button = page.get_by_role("link", name="Next", exact=True)
            if not next_button or not await next_button.is_enabled():
                break

            # Click "Next" and wait for the table content to change
            old_content = await page.evaluate(
                "document.querySelector('table tbody').innerHTML"
            )
            await next_button.click()
            page_counter += 1

            # Wait until the table content updates
            await page.wait_for_function(
                """
                (oldContent) => document.querySelector('table tbody').innerHTML !== oldContent
                """,
                arg=old_content,
            )
