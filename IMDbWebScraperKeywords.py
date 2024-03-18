"""
@author: Suraj.Maurya
created: 18/03/2024
"""
from SeleniumLibrary import SeleniumLibrary
import logging
import os
import time
import csv
import json
import argparse

class IMDbWebScraperKeywords(SeleniumLibrary):
    """
    IMDbWebScraperKeywords class facilitates scraping data from IMDb website.
    """

    def __init__(self):
        """
        Initializes IMDbWebScraper class.
        """
        super(IMDbWebScraperKeywords, self).__init__()
        self.logger = logging.getLogger(__name__)

    def set_row_separator(self, locator):
        """
        Sets the locator for identifying rows in the table.

        Args:
            locator (str): Locator for identifying rows in the table.
        """
        try:
            self.table_row_identifier_locator = locator.replace("xpath=", "")
            self.table_row_fields = []
            self.table_next_element = ''
            self.table_scrollable = False
            self.table_scrollable_reset = ''
            self.table_scroll_by = ''
        except Exception as e:
            self.logger.error("Error occurred while setting row separator locator: %s", str(e))
            raise e

    def add_column(self, locator, metadata):
        """
        Adds a column to the table.

        Args:
            locator (str): Locator for identifying the column.
            metadata (str): Metadata for the column in the format 'label::attribute'.
        """
        try:
            list_metadata = metadata.split('::')
            if len(list_metadata) != 2:
                raise ValueError('Invalid metadata %s' % metadata)

            table_column = {}
            table_column['label'] = list_metadata[0]
            table_column['attribute'] = list_metadata[1]
            table_column['locator_orig'] = locator
            table_column['locator'] = locator.replace("xpath=", "")
            self.table_row_fields.append(table_column)

        except Exception as e:
            self.logger.error("Error occurred while adding column: %s", str(e))
            raise e

    def set_next_page_button(self, locator, scrollable=False, scroll_by=0, scrollable_reset=0):
        """
        Sets the locator for the 'Next Page' button.

        Args:
            locator (str): Locator for identifying the 'Next Page' button.
            scrollable (bool): Flag indicating if scrolling is enabled.
            scroll_by (int): Scroll amount.
            scrollable_reset (int): Reset value for scrollable.
        """
        try:
            if locator is None or locator.strip() == '':
                raise ValueError('locator is required: ' + str(locator))

            self.table_next_element = locator.replace("xpath=", "")

            if scrollable is None or str(scrollable).strip() == '':
                self.table_scrollable = False
            elif str(scrollable).lower() == 'true' or scrollable == True:
                self.table_scrollable = True
            else:
                self.table_scrollable = False

            if scrollable_reset is None or str(scrollable_reset).strip() == '':
                scrollable_reset = 0
            if scroll_by is None or str(scroll_by).strip() == '':
                scroll_by = 0
            self.table_scrollable_reset = int(scrollable_reset)
            self.table_scroll_by = int(scroll_by)
        except Exception as e:
            self.logger.error("Error occurred while setting next page button: %s", str(e))
            raise e

    def wait_for_page_load(self, wait_time=30):
        """
        Waits for the page to be loaded completely.

        Args:
            wait_time (int): Maximum time to wait for page load.
        """
        try:
            for index in range(0, int(wait_time)):
                state = self.execute_javascript("return document.readyState")
                try:
                    jquery_state = self.execute_javascript("return jQuery.active")
                except:
                    jquery_state = 0

                if state != 'complete' or jquery_state != 0:
                    self.logger.info("Waiting for page to load")
                    time.sleep(1)
                else:
                    break
        except Exception as e:
            self.logger.error("Error occurred while waiting for page load: %s", str(e))
            raise e

    def scrape_table(self, no_of_rows, wait_time=30, file_path=''):
        """
        Scrapes data from the table.

        Args:
            no_of_rows (int): Number of rows to scrape.
            wait_time (int): Maximum time to wait for page load.
            file_path (str): File path to save the scraped data.

        Returns:
            list: List containing scraped data.
        """
        try:
            self.is_scrap = True
            list_data = []

            self.wait_for_page_load(int(wait_time))
            self.wait_until_page_contains_element("xpath=%s" % self.table_row_identifier_locator, wait_time)

            column_names = []
            for column_data in self.table_row_fields:
                column_names.append(column_data['label'])
            list_data.append(column_names)

            table_index = 1
            row_index = 0
            self.last_page_data = []
            self.current_page_data = []
            while no_of_rows == 0 or row_index < no_of_rows:
                col_data, table_reset, scroll_reset, stop, revert_last_page = self._get_table_row_data(table_index,
                                                                                                       wait_time)
                if scroll_reset:
                    table_index = table_index - int(self.table_scrollable_reset)
                if table_reset:
                    table_index = 0
                    self.wait_for_page_load(wait_time)
                if revert_last_page:
                    list_data = list_data[:(len(self.current_page_data) * -1)]
                if stop:
                    break
                if not (scroll_reset or table_reset):
                    list_data.append(col_data)
                    self.current_page_data.append(col_data)
                    row_index = row_index + 1
                table_index = table_index + 1
            self.logger.info("Number of Records scrapped : {0}".format(len(list_data) - 1))
            self.is_scrap = False
            self.convert_to_csv_and_json(list_data, file_path)
            return list_data
        except Exception as e:
            self.logger.error("Error occurred while scraping table: %s", str(e))
            raise e

    def _get_table_row_data(self, row_index, wait_time):
        """
        Retrieves data from table row.

        Args:
            row_index (int): Index of the row.
            wait_time (int): Maximum time to wait for page load.

        Returns:
            tuple: Tuple containing column values, flags indicating resets, and stop condition.
        """
        try:
            column_values = []
            reset = False
            scroll_reset = False
            stop = False
            revert_last_page = False
            try:
                row_element = self.find_element('xpath={0}[{1}]'.format(self.table_row_identifier_locator, row_index))
            except:
                self.logger.info("Next page on record: {0}".format((row_index - 1)))
                if self.table_next_element == '' and self.table_scrollable == False:
                    stop = True
                if self.table_scrollable:
                    try:
                        self.driver.execute_script("window.scrollBy( 0, arguments[0]);", self.table_scroll_by)
                    except Exception as e:
                        raise e
                    scroll_reset = True
                if self.table_next_element != '':
                    try:
                        if self._check_element_is_visible_and_enabled(self.table_next_element):
                            element = self.driver.find_element('xpath', self.table_next_element)
                            element.click()
                            time.sleep(2)
                            self.wait_for_page_load(wait_time)
                            reset = True
                        else:
                            self.logger.info("Next Page element disabled or not visible.")
                            stop = True
                            revert_last_page = True
                    except:
                        self.logger.info("Next Page element not found. Stopping iteration for rows.")
                        stop = True
                if stop == False:
                    time.sleep(1)
                    if len(self.current_page_data) == len(self.last_page_data):
                        is_different = False
                        for i in range(0, len(self.current_page_data)):
                            if is_different:
                                break
                            else:
                                for cur_index, cur_val in enumerate(self.current_page_data[i]):
                                    if cur_val != (self.last_page_data[i])[cur_index]:
                                        is_different = True
                                        break
                        if is_different:
                            reset = True
                            self.last_page_data = self.current_page_data
                            self.current_page_data = []
                        else:
                            self.logger.info(
                                "Same records for current and last page. Stopping and removing duplicate records.")
                            revert_last_page = True
                            stop = True
                    else:
                        reset = True
                        self.last_page_data = self.current_page_data
                        self.current_page_data = []

            if not (scroll_reset or stop or reset):
                for column_data in self.table_row_fields:
                    try:
                        col_element = self.find_element('xpath=' + column_data['locator'], parent=row_element)
                        if col_element.is_displayed():
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", col_element)
                        if column_data['attribute'].lower() == 'text':
                            att_val = col_element.text
                        else:
                            att_val = col_element.get_attribute(column_data['attribute'])
                    except:
                        att_val = ''
                    column_values.append(att_val)
            return column_values, reset, scroll_reset, stop, revert_last_page
        except Exception as e:
            self.logger.error("Error occurred while getting table row data: %s", str(e))
            raise e

    def _check_element_is_visible_and_enabled(self, locator):
        """
        Checks if element identified by the locator is visible and enabled.

        Args:
            locator (str): Locator for identifying the element.

        Returns:
            bool: True if element is visible and enabled, False otherwise.
        """
        try:
            element = self.driver.find_element('xpath', locator)

            if element.is_displayed() and element.is_enabled():
                self.logger.info("Locator is Visible and enabled :- %s" % locator)
                return True
            else:
                self.logger.info("Locator '%s' NOT Visible & enabled" % locator)
                raise Exception("Locator is not Visible and enabled")
        except Exception as e:
            self.logger.error("Error occurred while checking element visibility and enabled state: %s", str(e))
            raise e

    def convert_to_csv_and_json(self, data, file_path=''):
        """
        Converts data to CSV or JSON format and saves it to the specified file path.

        Args:
            data (list): List containing the data to be saved.
            file_path (str): File path to save the data.

        Returns:
            str: JSON formatted string of the cleaned data.
        """
        try:
            # Remove empty lists
            cleaned_data = [row for row in data if row != ['', '']]
            for index, sublist in enumerate(cleaned_data):
                if index == 0:
                    continue
                cleaned_data[index][1] = ''.join(filter(str.isdigit, str(sublist[1])))
                if "Director:" in sublist[3]:
                    cleaned_data[index][3] = sublist[3].split("Director: ")[1].split(" | ")[0]
                elif "Stars:" in sublist[3]:
                    cleaned_data[index][3] = ''
                if "Stars:" in sublist[4]:
                    cleaned_data[index][4] = sublist[4].split("Stars: ")[1].split(" | ")[0]
                elif "Director:" in sublist[4]:
                    cleaned_data[index][4] = ''

            file_path = os.path.normpath(file_path)
            file_extension = os.path.splitext(file_path)[1]

            if file_extension == '.csv':
                # Save as CSV
                with open(file_path, 'w', newline='') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    csv_writer.writerows(cleaned_data)
                self.logger.info(f"Data saved to '{file_path}'")
            elif file_extension == '.json':
                # Save as JSON
                with open(file_path, 'w') as jsonfile:
                    json.dump(cleaned_data, jsonfile)
                self.logger.info(f"Data saved to '{file_path}'")
            else:
                self.logger.info("Invalid output file path given: {}. Please provide '.csv' or '.json' file path.".format(file_path))
                raise ValueError("Invalid output file path given: {}. Please provide '.csv' or '.json' file path.".format(file_path))
            return json.dumps(cleaned_data)
        except Exception as e:
            self.logger.error("Error occurred while converting data to CSV or JSON: %s", str(e))
            raise e

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='IMDb Web Scraper')
    parser.add_argument('--keywords', type=str, default='movie', help='Title type of movie (default: movie)')
    parser.add_argument('--num_rows', type=int, default=50, help='Number of rows to scrape (default: 50)')
    parser.add_argument('--file_path', type=str, default='output.csv', help='File path to save the scraped data (default: output.csv)')
    args = parser.parse_args()

    try:
        obj = IMDbWebScraperKeywords()
        userinput = args.keywords.strip()
        file_path = args.file_path.strip()
        num_rows = args.num_rows

        obj.open_browser("https://www.imdb.com/search/keyword/?ref_=kw_ref_typ&sort=moviemeter,asc&mode=detail&page=1&title_type={0}".format(userinput), browser="chrome")
        obj.maximize_browser_window()
        time.sleep(1)
        obj.set_row_separator("(//*[normalize-space(text()) and normalize-space(.)='YourRating'])[1]/following::div[1]/div")
        obj.set_next_page_button('(//a[text()="Next »"])[2]')
        obj.add_column(".//h3/a", "Title::text")
        obj.add_column(".//span[@class='lister-item-year text-muted unbold']", "Release Year::text")
        obj.add_column(".//strong", "IMDb Rating::text")
        obj.add_column(".//p[3]", "Director(s)::text")
        obj.add_column(".//p[3]", "Cast::text")
        obj.add_column(".//p[2]", "Plot Summary::text")
        output = obj.scrape_table(num_rows, file_path=file_path)
    except Exception as e:
        print("An error occurred:", str(e))
