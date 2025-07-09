# Books Online Price Monitoring Program
On-demand data extraction program for use with [Books to Scrape](https://books.toscrape.com/). This program creates two folders with the following names and contents.
- **[yyyy.mm.dd]_images** contains a ‘.jpg’ image for each product found under Books to Scrape categories, named using the product’s UPC. A ‘.csv’ image key is also generated to connect images to their corresponding book titles.
- **[yyyy.mm.dd]_csv** contains one ‘.csv’ file per category. Each file includes a list of all products found under Books to Scrape's categories. 


## Prerequisites
[Python 3.13.5](https://www.python.org/downloads/)
-	Versions 3.9 and up should work for this program; 3.13 was used to develop the script.

## Installation
Use Microsoft CMD or Apple Terminal for any command prompts shown below.
1. Clone this repository to your local machine:
```git clone https://github.com/MichieMarie/Books_Online.git``` 
2. Install required Python packages:
```pip install -r requirements.txt```

## How to Run
1. Open a terminal or command prompt window.
2. Navigate to the folder where you saved the project: ```cd [path]\Books_Online```
3. Run the main script: ```python books_scraper.py```
4. The program will create two folders (see Output) 

## Output
- A folder with the naming structure yyyy.mm.dd_csv (e.g. ```2025.07.01_csv```) containing one CSV file per category. CSV files have the following fields for each product:
  1. product_page_url
  2. universal_ product_code (upc)
  3. book_title
  4. price_including_tax
  5. price_excluding_tax
  6. quantity_available
  7. product_description
  8. category
  9. review_rating
  10. image_url
- A folder with the naming structure yyyy.mm.dd_images (e.g. ```2025.07.01_images```) containing:
  - One JPG image per product named using the product's UPC
  - A CSV file, image_key.csv, mapping UPC codes and book titles

## Usage
This program allows the user to capture all prices (with and without tax) as posted by Books to Scrape on any given date. Books Online can use this data to compare prices, descriptions, and for stocking considerations (based on availability elsewhere).

Additionally, dates are included in the file names to assist future analysts in tracking book prices and product movement.




