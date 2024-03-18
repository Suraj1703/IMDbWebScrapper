try:
    from .IMDbWebScraperKeywords import IMDbWebScraperKeywords
except:
    from IMDbWebScrapper.IMDbWebScraperKeywords import IMDbWebScraperKeywords


class IMDbWebScraper(IMDbWebScraperKeywords):
    """
    IMDbWebScraper class facilitates scraping data from IMDb website.
    """
    def __init__(self):
        super().__init__()

