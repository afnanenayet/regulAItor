# scrapy crawlers

This subdirectory is a `scrapy` project, which is a Python library
for making web crawlers.

# Running

Run from this directory:

```bash
export URL_JSON=$(readlink -f .)/urls.json

uv runspider crawlers/spiders/fda_warning_link_spider.py -o "$URL_JSON"
uv run scrapy crawl warning_letter_contents
```
