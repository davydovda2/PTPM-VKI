import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


class ForumParser:

    def __init__(self, timeout=10):
        self.timeout = timeout
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    def fetch_page(self, url):
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return response.text

    def parse_page(self, url):
        html = self.fetch_page(url)
        return self.parse_html(html)

    def parse_pages(self, start_url, max_pages=5):
        posts = []
        url = start_url
        visited = set()
        page_number = 0

        while url and page_number < max_pages and url not in visited:
            visited.add(url)
            html = self.fetch_page(url)
            posts.extend(self.parse_html(html))
            url = self._get_next_page_url(html, url)
            page_number += 1

        return posts

    def _get_next_page_url(self, html, current_url):
        soup = BeautifulSoup(html, "lxml")
        next_link = soup.select_one("a.next, a[rel='next']")
        if next_link is None:
            return None

        href = next_link.get("href")
        if not href:
            return None

        return urljoin(current_url, href)

    def parse_html(self, html):
        soup = BeautifulSoup(html, "lxml")
        posts = []

        for post in soup.select("article.post, div.post"):
            comment_id = self._extract_id(post)
            name = self._extract_name(post)
            message = self._extract_message(post)

            if comment_id is None or not name or not message:
                continue

            posts.append(
                {
                    "id": comment_id,
                    "name": name,
                    "message": message,
                }
            )

        return posts

    def _extract_id(self, post):
        raw_id = post.get("data-post-id")
        if raw_id and raw_id.strip().isdigit():
            return int(raw_id)

        post_id = post.get("id", "")
        match = re.search(r"post-(\d+)", post_id)
        if match:
            return int(match.group(1))

        permalink = post.select_one("a.permalink")
        if permalink:
            href = permalink.get("href", "")
            match = re.search(r"(?:p=|post-)(\d+)", href)
            if match:
                return int(match.group(1))

        return None

    def _extract_name(self, post):
        author = post.select_one(".post-author .username")
        if author is None:
            author = post.select_one(".username")
        if author is None:
            author = post.select_one(".author")

        if author is None:
            return None
        return author.get_text(strip=True)

    def _extract_message(self, post):
        message = post.select_one(".post-message")
        if message is None:
            message = post.select_one(".message")

        if message is None:
            return None
        return message.decode_contents().strip()

    def save_to_db(self, parsed_data, repository):
        saved = 0
        for post in parsed_data:
            repository.add(post["id"], post["name"], post["message"])
            saved += 1
        return saved
