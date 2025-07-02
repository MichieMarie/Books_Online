import requests
from bs4 import BeautifulSoup
import csv

SITE_URL = 'http://books.toscrape.com/'

def get_categories():
    """Returns names and URLs of all categories from the homepage."""
    site_page = requests.get(SITE_URL)
    site_soup = BeautifulSoup(site_page.content, "html.parser")
    categories = []

    for cat in site_soup.select("ul.nav.nav-list > li > ul > li > a"):
        category_name = cat.text.strip()
        category_url = SITE_URL + cat["href"]
        categories.append((category_url, category_name))

    return categories



def get_product_page_urls(category_url):
    '''Returns a list of product page URLs from each category including additional pages.'''
    product_page_urls = []

    while category_url:
        page = requests.get(category_url)
        soup = BeautifulSoup(page.content, "html.parser")

        for book in soup.select("li.col-xs-6.col-sm-4.col-md-3.col-lg-3"):
            href = book.find("h3").find("a")["href"]
            url = SITE_URL + "catalogue/" + href[9:]
            product_page_urls.append(url)

        # pagination - check for next page once per page
        next_link = soup.select_one("li.next a")
        if next_link:
            next_href = next_link["href"]
            category_url = category_url.rsplit("/", 1)[0] + "/" + next_href
        else:
            category_url = None

    return product_page_urls



def get_book_html(url):
    '''Fetches HTML from book page and returns BS object.'''
    page = requests.get(url)
    page_soup = BeautifulSoup(page.content, 'html.parser')

    return page_soup

# Functions to scrape product pages
def get_tbl_data(soup):
    '''Product page table data for upc, price w & w/o taxes, and availability.
    Clean availability str to just numbers.'''
    table_data = soup.select('table.table tr td')
    universal_product_code = table_data[0].text.strip()
    price_including_tax = table_data[3].text.strip()
    price_excluding_tax = table_data[2].text.strip()
    availability_text = table_data[5].text.strip()

    quantity_available = next((word.strip('()') for word in availability_text.split() if word.strip('()').isdigit()), '0')

    return universal_product_code, price_including_tax, price_excluding_tax, quantity_available


def get_title(soup):
    '''Scrape book title from product page.'''
    title_parent = soup.find('h1')
    book_title = title_parent.text.strip()
    return book_title


def get_description(soup):
    '''Scrape book description from product page.'''

    paragraphs = soup.select('article.product_page p')
    if len(paragraphs) > 3:
        return paragraphs[3].text.strip()
    else:
        return ''



def get_review_rating(soup):
    '''Scrape review from product page.'''
    rtg_parent = soup.find('p', class_='star-rating')
    rtg_tags = rtg_parent['class']
    review_rating = rtg_tags[1]
    return review_rating


def get_img_url(soup):
    '''Scrape image url from product page.'''
    img_src = soup.select_one('div.item.active img')['src']
    return SITE_URL + img_src[6:]

def get_categorized_books(category_url, category_name):
    product_page_urls = get_product_page_urls(category_url)
    category_books_data = []

    for url in product_page_urls:
        soup = get_book_html(url)
        universal_product_code, price_including_tax, price_excluding_tax, quantity_available = get_tbl_data(soup)

        book_dict = {'product_page_url': url, 'universal_product_code': universal_product_code,
                         'book_title': get_title(soup), 'price_including_tax': price_including_tax,
                         'price_excluding_tax': price_excluding_tax, 'quantity_available': quantity_available,
                         'product_description': get_description(soup), 'category': category_name,
                         'review_rating': get_review_rating(
                             soup),
                         'image_url': get_img_url(soup)}

        category_books_data.append(book_dict)  # append active iteration of book_dict to list of category dictionaries

    return category_books_data


def main():
    for category_url, category_name in get_categories():
        category_books_data = get_categorized_books(category_url, category_name)
        save_to_csv(category_books_data, category_name)

def save_to_csv(category_books_data, category_name):
    csv_filename = f'../CSV_files/{category_name}.csv'
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['product_page_url', 'universal_product_code', 'book_title', 'price_including_tax',
                      'price_excluding_tax', 'quantity_available', 'product_description', 'category', 'review_rating',
                      'image_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(category_books_data)


if __name__ == '__main__':
    main()