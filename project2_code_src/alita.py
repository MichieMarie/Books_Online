import requests
from bs4 import BeautifulSoup
import csv

site_url = "http://books.toscrape.com/" #captures Books to Scrape url
product_page_url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html" # url for one book
page = requests.get(product_page_url)
soup = BeautifulSoup(page.content, "html.parser")

# Creating a dictionary for the csv and adding the first pair
alita_data = {}
alita_data['product_page_url'] = product_page_url

# Scraping the table at the bottom of the page for UPC, price w and w/o tax, and availability
info_tbl = soup.find("table", class_="table")
info_rows = info_tbl.find_all("tr")

# UPC
universal_product_code = info_rows[0].find_all("td")[0].text.strip() #upc is in the first td of first row
alita_data['universal_product_code'] = universal_product_code
#print("UPC:", universal_product_code)

# Capture the title
title_parent = soup.find("h1") # finds title which is listed near top under the body
book_title = title_parent.text.strip() #strips white space
alita_data['book_title'] = book_title
#print("Book title:", book_title)

# Price with tax
price_including_tax = info_rows[3].find_all("td")[0].text.strip()
alita_data['price_including_tax'] = price_including_tax
#print("Price including tax:", price_including_tax)

# Price before tax
price_excluding_tax = info_rows[2].find_all("td")[0].text.strip()
alita_data['price_excluding_tax'] = price_excluding_tax
#print("Price excluding tax:", price_excluding_tax)

# Availability
quantity_available = info_rows[5].find_all("td")[0].text.strip()
quantity_available = quantity_available[10:13]
alita_data['quantity_available'] = quantity_available
#print("Quantity available:", quantity_available)

# Capture the description
prod_desc_parent = soup.find("article", class_="product_page") #Identifies parent of description
prod_desc_next = prod_desc_parent.find_all("p") # description listed under a <p> tag
product_description = prod_desc_next[3].text.strip() # strips white space and captures 4th <p>
alita_data['product_description'] = product_description
#print("Product description:", product_description)

# Capture the category
cat_parent = soup.find("ul", class_="breadcrumb") # finds category which is a link on the page
cat_link = cat_parent.find_all("a") #category listed under an <a> tag
category = cat_link[2].text.strip() #strips white space and captures 3rd <a>
alita_data['category'] = category
#print("Category:", category)

# Review rating
rtg_parent = soup.find("p", class_="star-rating")
rtg_tags =  rtg_parent["class"]
review_rating = rtg_tags[1]
alita_data['review_rating'] = review_rating
#print("Review rating:", review_rating)

# Product image url
img_parent = soup.find("div", class_="item active") #finds img parent class
img_tag = img_parent.find("img") # finds img tag
img_src = img_tag["src"] #identifies partial url in tag
img_src = img_src[6:] # removes '../../' from partial html url
image_url = site_url + img_src # builds full url link
alita_data['image_url'] = image_url
#print("Image url:", image_url)

#print(alita_data)

# build csv output
with open('alita.csv', mode='w') as csvfile:
    fieldnames = alita_data.keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerow(alita_data)


