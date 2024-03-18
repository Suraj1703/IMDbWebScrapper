# IMDb Web Scraper

## Overview
This Python script allows you to scrape movie information from IMDb based on specific genres or keywords.

## How to Run
1. Clone this repository.
2. `requirements.txt` includes the necessary dependencies. You can install them using pip: pip install -r requirements.txt
3. Run the script with the desired parameters.
Specify the --keywords parameter to specify the title type of movies (default: movie).
Specify the --file_path parameter to specify the file path to save the scraped data (default: output.csv).
Example usage:
python IMDbWebScrapper\IMDbWebScraperKeywords.py --keywords movie --file_path E:\\output.csv

## Dependencies
- Python 3.x
- robotframework-seleniumlibrary
- selenium
- Chrome WebDriver (chromedriver)

## Script Functionalities
- Scrapes movie details such as title, release year, IMDb rating, director(s), cast and Plot Summary.
- Handles pagination to extract data from multiple pages.
- Saves the extracted data in CSV format and Json file format based on user choice.

## Bonus Functionalities
- Error handling and logging to handle unexpected issues gracefully.

## Configuration
- You can adjust settings like browser choice and output file path directly in the script.

## Unit Tests
- Unit tests have been implemented to validate the functionality of the scraper.

## Author
- Suraj.Maurya