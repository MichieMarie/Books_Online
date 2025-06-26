import requests
from bs4 import BeautifulSoup
import csv

site_url = "http://books.toscrape.com/"
product_category_url = "https://books.toscrape.com/catalogue/category/books/poetry_23/index.html"  # url for poetry books


# Build list of product page urls.
def get_poetry_urls():
    """Returns a list of product page URLs from the poetry category page."""
    poetry_page = requests.get(product_category_url)
    poetry_soup = BeautifulSoup(poetry_page.content, "html.parser")

    return [site_url + "catalogue/" + book.find("h3").find("a")["href"][9:] for book in poetry_soup.select("li.col-xs-6.col-sm-4.col-md-3.col-lg-3")]

def get_book_urls(url):
    """Fetches HTML from book page and returns BS object."""
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    return soup

# Functions to scrape product pages
def get_tbl_data(soup):
    """Product page table data for upc, price w & w/o taxes, and availability.
    Clean availability str to just numbers."""
    table_data = soup.select("table.table tr td")
    universal_product_code = table_data[0].text.strip()
    price_including_tax = table_data[3].text.strip()
    price_excluding_tax = table_data[2].text.strip()
    availability_text = table_data[5].text.strip()

    quantity_available = next((word.strip("()") for word in availability_text.split() if word.strip("()").isdigit()), "0")

    return universal_product_code, price_including_tax, price_excluding_tax, quantity_available


def get_title(soup):
    """Scrape book title from product page."""
    title_parent = soup.find("h1")
    book_title = title_parent.text.strip()
    return book_title


def description(soup):
    """Scrape book description from product page."""
    prod_desc_parent = soup.find("article", class_="product_page")
    prod_desc_next = prod_desc_parent.find_all("p")
    product_description = prod_desc_next[3].text.strip()
    return product_description


def category(soup):
    """Scrape book category from product page."""
    cat_parent = soup.find("ul", class_="breadcrumb")
    cat_link = cat_parent.find_all("a")
    category = cat_link[2].text.strip()
    return category


def review(soup):
    """Scrape review from product page."""
    rtg_parent = soup.find("p", class_="star-rating")
    rtg_tags = rtg_parent["class"]
    review_rating = rtg_tags[1]
    return review_rating


def img_url(soup):
    """Scrape image url from product page."""
    img_parent = soup.find("div", class_="item active")
    img_tag = img_parent.find("img")  # finds img tag
    img_src = img_tag["src"]  # identifies partial url in tag
    img_src = img_src[6:]  # removes '../../' from partial html url
    image_url = site_url + img_src  # builds full url link
    return image_url

# Building product dictionaries
poetry_books_data = []  # list for all poetry book dictionaries

product_page_urls = get_poetry_urls()
for url in product_page_urls:
    soup = get_book_urls(url)
    universal_product_code, price_including_tax, price_excluding_tax, quantity_available = get_tbl_data(soup)

    book_dict = {'product_page_url': url, 'universal_product_code': universal_product_code,
                 'book_title': get_title(soup), 'price_including_tax': price_including_tax,
                 'price_excluding_tax': price_excluding_tax, 'quantity_available': quantity_available,
                 'product_description': description(soup), 'category': category(soup), 'review_rating': review(soup),
                 'image_url': img_url(soup)}

    poetry_books_data.append(book_dict)  # append active iteration of book_dict to list of poetry dictionaries

# build csv output and save to file
with open('../CSV_files/poetry.csv', mode='w', newline="") as csvfile:
    fieldnames = ['product_page_url', 'universal_product_code', 'book_title', 'price_including_tax',
                  'price_excluding_tax', 'quantity_available', 'product_description', 'category', 'review_rating',
                  'image_url']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(poetry_books_data)
