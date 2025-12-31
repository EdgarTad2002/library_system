import requests
from django.core.files.base import ContentFile
import os
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from django.contrib.auth.mixins import UserPassesTestMixin
from .models import Book, Category
from django.utils.text import slugify

class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser
    
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; BookScraper/1.0)"
}

def fetch_html(url):
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response.text


def parse_book_detail(book_url):
    html = fetch_html(book_url)
    soup = BeautifulSoup(html, "html.parser")

    title = soup.find("h1").text.strip()

    description_tag = soup.select_one("#product_description ~ p")
    description = description_tag.text.strip() if description_tag else ""

    category = soup.select("ul.breadcrumb li a")[-1].text.strip()

    availability_text = soup.select_one(".availability").text.strip()
    copies = int("".join(filter(str.isdigit, availability_text)) or 1)

    image_relative_url = soup.select_one(".item.active img")["src"]
    image_url = urljoin(book_url, image_relative_url)

    return {
        "title": title,
        "author": "Unknown",
        "content": description,
        "publisher": "Unknown",
        "categories": [category],
        "copies_available": copies,
        "source_url": book_url,
        "image_url": image_url,
    }

def download_image(image_url):
    response = requests.get(image_url, timeout=10)
    response.raise_for_status()
    return ContentFile(response.content)


def parse_listing_page(page_url):
    html = fetch_html(page_url)
    soup = BeautifulSoup(html, "html.parser")

    books = []
    for article in soup.select(".product_pod"):
        relative_url = article.h3.a["href"]
        book_url = urljoin(page_url, relative_url)
        books.append(book_url)

    return books


def scrape_books(max_pages=2, delay=1):
    """
    Scrape books and return list of dicts
    """
    base_url = "https://books.toscrape.com/catalogue/page-{}.html"
    scraped_books = []
    isbn_counter = 1000000

    for page in range(1, max_pages + 1):
        page_url = base_url.format(page)
        print(f"Scraping page {page}")

        try:
            book_urls = parse_listing_page(page_url)
        except Exception as e:
            print("Failed page:", e)
            continue

        for book_url in book_urls:
            try:
                book_data = parse_book_detail(book_url)
                book_data["isbn"] = f"AUTO-{isbn_counter}"
                isbn_counter += 1
                scraped_books.append(book_data)
                time.sleep(delay)
            except Exception as e:
                print("Failed book:", book_url, e)

    return scraped_books


def save_books_to_db(scraped_books):
    created_count = 0
    updated_count = 0

    for item in scraped_books:
        book, created = Book.objects.update_or_create(
            source_url=item["source_url"],
            defaults={
                "title": item["title"],
                "author": item.get("author", "Unknown"),
                "content": item.get("content", ""),
                "publisher": item.get("publisher", "Unknown"),
                "isbn": item["isbn"],
                "copies_available": item.get("copies_available", 1),
                "is_scraped": True,
                "slug": slugify(item["title"])[:100],
            }
        )

        # ✅ SAVE IMAGE ONLY IF NOT ALREADY SAVED
        if item.get("image_url") and not book.photo:
            image_content = download_image(item["image_url"])
            image_name = os.path.basename(item["image_url"])
            book.photo.save(image_name, image_content, save=True)

        # Categories
        book.category.clear()
        for cat_name in item["categories"]:
            category, _ = Category.objects.get_or_create(
                name=cat_name,
                defaults={"slug": slugify(cat_name)}
            )
            book.category.add(category)

        if created:
            created_count += 1
        else:
            updated_count += 1

    return created_count, updated_count