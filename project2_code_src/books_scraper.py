import requests
from bs4 import BeautifulSoup
import csv

site_url = "http://books.toscrape.com/"
product_category_url = "https://books.toscrape.com/catalogue/category/books/poetry_23/index.html"  # url for poetry books


# Build list of product page urls.
def get_product_page_urls():
    """Returns a list of product page URLs from the poetry category page."""
    poetry_page = requests.get(product_category_url)
    poetry_soup = BeautifulSoup(poetry_page.content, "html.parser")

    return [site_url + "catalogue/" + book.find("h3").find("a")["href"][9:] for book in poetry_soup.select("li.col-xs-6.col-sm-4.col-md-3.col-lg-3")]

def get_book_urls(url):
    """Fetches HTML from book page and returns BS object."""
    page = requests.get(url)
    page_soup = BeautifulSoup(page.content, "html.parser")

    return page_soup

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


def get_description(soup):
    """Scrape book description from product page."""

    paragraphs = soup.select("article.product_page p")
    if len(paragraphs) > 3:
        return paragraphs[3].text.strip()
    else:
        return ""


def get_category(soup):
    """Scrape book category from product page, if available."""
    category_links = soup.select("ul.breadcrumb a")
    if len(category_links) > 2:
        return category_links[2].text.strip()
    else:
        return ""


def get_review_rating(soup):
    """Scrape review from product page."""
    rtg_parent = soup.find("p", class_="star-rating")
    rtg_tags = rtg_parent["class"]
    review_rating = rtg_tags[1]
    return review_rating


def get_img_url(soup):
    """Scrape image url from product page."""
    img_src = soup.select_one("div.item.active img")["src"]
    return site_url + img_src[6:]

# Building product dictionaries
poetry_books_data = []  # list for all poetry book dictionaries


for url in get_product_page_urls():
    soup = get_book_urls(url)
    universal_product_code, price_including_tax, price_excluding_tax, quantity_available = get_tbl_data(soup)

    book_dict = {'product_page_url': url, 'universal_product_code': universal_product_code,
                 'book_title': get_title(soup), 'price_including_tax': price_including_tax,
                 'price_excluding_tax': price_excluding_tax, 'quantity_available': quantity_available,
                 'product_description': get_description(soup), 'category': get_category(soup), 'review_rating': get_review_rating(
            soup),
                 'image_url': get_img_url(soup)}

    poetry_books_data.append(book_dict)  # append active iteration of book_dict to list of poetry dictionaries

def save_to_csv(poetry_books_data):
    with open('../CSV_files/poetry.csv', mode='w', newline="") as csvfile:
        fieldnames = ['product_page_url', 'universal_product_code', 'book_title', 'price_including_tax',
                      'price_excluding_tax', 'quantity_available', 'product_description', 'category', 'review_rating',
                      'image_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(poetry_books_data)
