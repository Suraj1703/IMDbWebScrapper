import unittest
from IMDbWebScrapper.IMDbWebScraperKeywords import IMDbWebScraperKeywords

class TestIMDbWebScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = IMDbWebScraperKeywords()

    def test_set_row_separator(self):
        self.scraper.set_row_separator("//some/locator")
        self.assertEqual(self.scraper.table_row_identifier_locator, "//some/locator")

    def test_add_column(self):
        self.scraper.set_row_separator("//some/locator")
        self.scraper.add_column("//column/locator", "Label::attribute")
        self.assertEqual(len(self.scraper.table_row_fields), 1)
        self.assertEqual(self.scraper.table_row_fields[0]['label'], "Label")
        self.assertEqual(self.scraper.table_row_fields[0]['attribute'], "attribute")
        self.assertEqual(self.scraper.table_row_fields[0]['locator_orig'], "//column/locator")

    def test_set_next_page_button(self):
        self.scraper.set_next_page_button("//next/button", True, 100, 5)
        self.assertEqual(self.scraper.table_next_element, "//next/button")
        self.assertTrue(self.scraper.table_scrollable)
        self.assertEqual(self.scraper.table_scroll_by, 100)
        self.assertEqual(self.scraper.table_scrollable_reset, 5)

    def test_wait_for_page_load(self):
        pass # Testing wait_for_page_load might require mocking, since it interacts with the browser.

    # Add more tests as needed

if __name__ == "__main__":
    unittest.main()
