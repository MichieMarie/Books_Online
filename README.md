# Books_Online Price Monitoring Program
On-demand data extraction program for use with [Books to Scrape](https://books.toscrape.com/). This program creates two folders with the following names and contents.
- **[yyyy.mm.dd]_csv** has one ‘.csv’ file per category. Each file contains a list of all category products and data, including UPC, price, and product URL.
- **[yyyy.mm.dd]_images** contains a ‘.jpg’ image for each product found in the categories noted above, named using a product’s UPC. A ‘.csv’ image key is also generated to connect images to their corresponding book titles.

## Prerequisites
[Python 3.13.5](https://www.python.org/downloads/)
-	Versions 3.9 and up may work for this program; 3.13 was used in creating the script.

## Installation
Use Microsoft CMD or Apple Terminal for any command prompts given below.
1. Clone this repository to your local machine:
```bash git clone https://github.com/MichieMarie/Books_Online.git``` 
2. Install required Python packages:
```pip install -r requirements.txt```

## How to Run
1. Open a terminal or command prompt window.
2. Navigate to the folder where you saved your script: ```cd [path]\Books_Online```


