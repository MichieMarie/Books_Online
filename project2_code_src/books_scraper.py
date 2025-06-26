import requests
from bs4 import BeautifulSoup
import csv

site_url = "http://books.toscrape.com/" #captures Books to Scrape url
product_category_url = "https://books.toscrape.com/catalogue/category/books/poetry_23/index.html" # url for poetry books
poetry_page = requests.get(product_category_url)
poetry_soup = BeautifulSoup(poetry_page.content, "html.parser")

# Build list of product page urls.
product_page_urls = []
book_parent = poetry_soup.find_all("li", class_="col-xs-6 col-sm-4 col-md-3 col-lg-3") #Finds url parent

for book in book_parent:
    url_tag = book.find("h3").find("a")
    urls = url_tag["href"]
    url = site_url + "catalogue/" + urls[9:]
    product_page_urls.append(url)

def get_tbl_data(soup):
    """Product page table data for upc, price w & w/o taxes, and availability.
    Clean availability str to just numbers."""
    info_tbl = soup.find("table", class_="table")
    info_rows = info_tbl.find_all("tr")
    universal_product_code = info_rows[0].find_all("td")[0].text.strip()
    price_including_tax = info_rows[3].find_all("td")[0].text.strip()
    price_excluding_tax = info_rows[2].find_all("td")[0].text.strip()
    available_wText = info_rows[5].find_all("td")[0].text.strip()
    for word in available_wText.split():
        cleaned_word = word.strip("()")  # remove parentheses
        if cleaned_word.isdigit():
            quantity_available = cleaned_word
            break
    else:
        quantity_available = "0"
    return universal_product_code, price_including_tax, price_excluding_tax, quantity_available


def get_title(soup):
    """Scrape book title from product page."""
    title_parent = soup.find("h1")
    book_title = title_parent.text.strip()
    return book_title

def description(soup):
    """Scrape book description from product page."""
    prod_desc_parent = soup.find("article", class_="product_page")  # Identifies parent of description
    prod_desc_next = prod_desc_parent.find_all("p")  # description listed under a <p> tag
    product_description = prod_desc_next[3].text.strip()  # strips white space and captures 4th <p>
    return product_description

def category(soup):
    """Scrape book category from product page."""
    cat_parent = soup.find("ul", class_="breadcrumb")  # finds category which is a link on the page
    cat_link = cat_parent.find_all("a")  # category listed under an <a> tag
    category = cat_link[2].text.strip()  # strips white space and captures 3rd <a>
    return category

def review(soup):
    """Scrape review from product page."""
    rtg_parent = soup.find("p", class_="star-rating")
    rtg_tags = rtg_parent["class"]
    review_rating = rtg_tags[1]
    return review_rating

def img_url(soup):
    """Scrape image url from product page."""
    img_parent = soup.find("div", class_="item active")  # finds img parent class
    img_tag = img_parent.find("img")  # finds img tag
    img_src = img_tag["src"]  # identifies partial url in tag
    img_src = img_src[6:]  # removes '../../' from partial html url
    image_url = site_url + img_src  # builds full url link
    return image_url

poetry_books_data = [] # list for all poetry book dictionaries

for url in product_page_urls:
    book_dict = {}  # creating the dictionary base for each book
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    get_tbl_data(soup)
    get_title(soup)
    description(soup)
    category(soup)
    review(soup)
    img_url(soup)

    book_dict = {'product_page_url': url, 'universal_product_code': get_tbl_data(soup)[0], 'book_title': get_title(soup), 'price_including_tax': get_tbl_data(soup)[1], 'price_excluding_tax': get_tbl_data(soup)[2], 'quantity_available': get_tbl_data(soup)[3], 'product_description' : description(soup), 'category' : category(soup), 'review_rating' : review(soup), 'image_url' : img_url(soup)}

    # book_dict[
    # book_dict[] = get_title(soup)
    # book_dict[] =
    # book_dict[] = get_tbl_data(soup)[1]
    # book_dict[] = get_tbl_data(soup)[2]
    # book_dict[] = get_tbl_data(soup)[3]
    # book_dict[] = description(soup)
    # book_dict['category'] = category(soup)
    # book_dict['review'] = review(soup)
    # book_dict['img_url'] = img_url(soup)

    poetry_books_data.append(book_dict) # append active iteration of book_dict to list of poetry dictionaries


# build csv output and
with open('../CSV_files/poetry.csv', mode='w', newline="") as csvfile:
    fieldnames = ['product_page_url', 'universal_product_code', 'book_title', 'price_including_tax', 'price_excluding_tax', 'quantity_available', 'product_description', 'category', 'review_rating', 'image_url']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(poetry_books_data)



