import scrapy


class WarningLetterItem(scrapy.Item):
    url = scrapy.Field()
    """URL letter was extracted from."""
    file_name = scrapy.Field()
    """We use the last part of the URL as the file name."""
    content = scrapy.Field()
    """Text content of the letter."""
