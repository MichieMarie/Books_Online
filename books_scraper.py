import requests
from bs4 import BeautifulSoup
import csv
from pathlib import Path
from datetime import datetime


date_string = datetime.now().strftime('%Y.%m.%d')

SITE_URL = 'http://books.toscrape.com/'
IMAGES_DIR = Path(f'{date_string}_images')
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
CSV_DIR = Path(f'{date_string}_csv')
CSV_DIR.mkdir(parents=True, exist_ok=True)

def get_categories() -> list[tuple[str, str]]:
    """
    Scrapes books.toscrape.com home page to retrieve all category names and their URLs.

    Returns:
        list[tuple[str, str]]: A list of (category name, category URL) tuples.
    """
    site_page = requests.get(SITE_URL)
    site_soup = BeautifulSoup(site_page.content, "html.parser")
    categories = []

    for cat in site_soup.select("ul.nav.nav-list > li > ul > li > a"):
        category_name = cat.text.strip()
        category_url = SITE_URL + cat["href"]
        categories.append((category_url, category_name))

    return categories


def get_product_page_urls(category_url: str) -> list[str]:
    '''
    Retrieves all product page URLs from a category URL, including paginated subpages.

    Args:
        category_url (str): URL of the category page to start scraping from.

    Returns:
        list[str]: A list of full URLs to each product page.
    '''

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


def get_book_html(url:str) -> BeautifulSoup:
    '''
    Fetches HTML from product page and returns a BeautifulSoup object.

    Args:
        url (str): URL of the product page.

    Returns:
        BeautifulSoup: A BeautifulSoup object containing the product page content.
    '''

    page = requests.get(url)
    page_soup = BeautifulSoup(page.content, 'html.parser')

    return page_soup


def get_tbl_data(soup: BeautifulSoup) -> list[tuple[str, str, str, str]]:
    '''
    Extracts upc, price w & w/o taxes, and availability from the product page table.

    Args:
        soup (BeautifulSoup): Parsed HTML of the product page.

    Returns:
        t[str, str, str, str]: A tuple containing:
            - UPC
            - Price including tax
            - Price excluding tax
            - Quantity available
    '''

    table_data = soup.select('table.table tr td')
    universal_product_code = table_data[0].text.strip()
    price_including_tax = table_data[3].text.strip()
    price_excluding_tax = table_data[2].text.strip()
    availability_text = table_data[5].text.strip()

    quantity_available = next((word.strip('()') for word in availability_text.split() if word.strip('()').isdigit()), '0')

    return universal_product_code, price_including_tax, price_excluding_tax, quantity_available


def get_title(soup: BeautifulSoup) -> str:
    '''
    Retrieves product page title.

    Args:
        soup (BeautifulSoup): Parsed HTML of the product page.

    Returns:
        str: Product page title.
    '''

    title_parent = soup.find('h1')
    book_title = title_parent.text.strip()

    return book_title


def get_description(soup: BeautifulSoup) -> str:
    '''
    Retrieves product description from product page.

    Args:
        soup (BeautifulSoup): Parsed HTML of the product page.

    Returns:
        str: Product description, or an empty string if no description was found.
    '''

    paragraphs = soup.select('article.product_page p')
    if len(paragraphs) > 3:
        return paragraphs[3].text.strip()
    else:
        return ''


def get_review_rating(soup: BeautifulSoup) -> str:
    '''
    Retrieves product review rating from product page.

    Args:
        soup (BeautifulSoup): Parsed HTML of the product page.

    Returns:
        str: Product review rating as a word (e.g., "One", "Two",...).
    '''

    rtg_parent = soup.find('p', class_='star-rating')
    rtg_tags = rtg_parent['class']
    review_rating = rtg_tags[1]

    return review_rating


def get_img_url(soup: BeautifulSoup) -> str:
    '''
    Retrieves product image domain extension from product page and concatenates it with site URL.

    Args:
        soup (BeautifulSoup): Parsed HTML of the product page.

    Returns:
        str: Product image domain extension.
    '''

    img_src = soup.select_one('div.item.active img')['src']
    img_url = SITE_URL + img_src[6:]

    return img_url


def get_categorized_books(category_url: str, category_name: str) -> list[dict]:
    '''
    Scrapes all product pages for a given category and returns a list of dictionaries containing product details. Also downloads each product image.

    Args:
        category_url (str): URL of the category page to start scraping from.
        category_name (str): Name of the product category to start scraping from.

    Returns:
        list[dict]: A list of dictionaries containing product details for the category.
    '''

    product_page_urls = get_product_page_urls(category_url)
    category_books_data = []

    for url in product_page_urls:
        soup = get_book_html(url)
        universal_product_code, price_including_tax, price_excluding_tax, quantity_available = get_tbl_data(soup)
        title = get_title(soup)
        img_url = get_img_url(soup)

        #download images
        image_filename = IMAGES_DIR / f"{universal_product_code}.jpg"
        download_image(img_url, image_filename)

        book_dict = {
            'product_page_url': url,
            'universal_product_code': universal_product_code,
            'book_title': title,
            'price_including_tax': price_including_tax,
            'price_excluding_tax': price_excluding_tax,
            'quantity_available': quantity_available,
            'product_description': get_description(soup),
            'category': category_name,
            'review_rating': get_review_rating(soup),
            'image_url': img_url
        }

        category_books_data.append(book_dict)  # append active iteration of book_dict to list of category dictionaries

    return category_books_data


def save_image_key_csv(image_key_data: list[tuple[str, str]]) -> str:
    '''
    Saves image_key.csv, linking product titles to UPCs.

    Args:
        image_key_data (list[tuple[str, str]]): A list of (product title, UPC) pairs.

    Returns:
        str: The path to the saved CSV file as a string.
    '''

    csv_filename = IMAGES_DIR / "image_key.csv"
    with open(csv_filename, mode='w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['book_title', 'universal_product_code'])
        writer.writerows(image_key_data)

    return csv_filename


def download_image(img_url: str, filename: Path) -> None:
    '''
    Downloads an image from the specified product page and saves it to the specified file path.

    Args:
        img_url (str): URL of the product page.
        filename (Path): Path to the file where the image will be saved.

    Returns:
        None
    '''

    response = requests.get(img_url)
    response.raise_for_status()
    with open(filename, 'wb') as f:
        f.write(response.content)


def save_to_csv(category_books_data: list[dict], category_name: str) -> None:
    '''
    Saves product data for a given category into a CSV file.

    Args:
        category_books_data (list[dict]): A list of dictionaries containing product data.
        category_name (str): The name of the category used to name the CSV file.

    Returns:
        None
    '''

    csv_filename = CSV_DIR / f"{category_name}.csv"
    with open(csv_filename, mode='w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['product_page_url', 'universal_product_code', 'book_title', 'price_including_tax',
                      'price_excluding_tax', 'quantity_available', 'product_description', 'category', 'review_rating',
                      'image_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(category_books_data)


def main():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    image_key_data = []

    for category_url, category_name in get_categories():
        category_books_data = get_categorized_books(category_url, category_name)

        # Build image key rows
        image_key_data.extend([(book['book_title'], book['universal_product_code']) for book in category_books_data])

        save_to_csv(category_books_data, category_name)

    save_image_key_csv(image_key_data)


if __name__ == '__main__':
    main()