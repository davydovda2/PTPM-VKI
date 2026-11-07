import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from src.database import DatabaseRepository
from src.parser import ForumParser

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


class ForumParserTestCase(unittest.TestCase):

    def setUp(self):
        self.parser = ForumParser()
        fixture_path = FIXTURES_DIR / "forum_page.html"
        self.fixture_html = fixture_path.read_text(encoding="utf-8")

    def _make_response(self, html):
        response = Mock()
        response.text = html
        response.raise_for_status = Mock()
        return response

    def test_parse_html_finds_all_posts(self):
        posts = self.parser.parse_html(self.fixture_html)

        self.assertEqual(len(posts), 3)
        self.assertEqual([post["id"] for post in posts], [101, 102, 103])

    def test_parse_html_extracts_name_and_message(self):
        posts = self.parser.parse_html(self.fixture_html)

        first_post = posts[0]
        self.assertEqual(first_post["name"], "ivan_petrov")
        self.assertIn("замокать", first_post["message"])

        second_post = posts[1]
        self.assertEqual(second_post["name"], "python_guru")
        self.assertIn("unittest.mock.patch", second_post["message"])

    def test_parse_html_keeps_inner_markup(self):
        posts = self.parser.parse_html(self.fixture_html)

        second_message = posts[1]["message"]
        self.assertIn("<b>unittest.mock.patch</b>", second_message)
        self.assertIn("<code>", second_message)

    def test_parse_html_returns_empty_list_for_empty_page(self):
        posts = self.parser.parse_html("<html><body></body></html>")
        self.assertEqual(posts, [])

    def test_parse_html_skips_incomplete_posts(self):
        html = """
        <article class="post" data-post-id="1">
            <div class="post-author"><span class="username">user</span></div>
        </article>
        <article class="post" data-post-id="2">
            <div class="post-author"><span class="username">user</span></div>
            <div class="post-message">Нормальное сообщение</div>
        </article>
        """
        posts = self.parser.parse_html(html)

        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["id"], 2)

    def test_parse_html_takes_id_from_element_id(self):
        html = """
        <div class="post" id="post-777">
            <div class="post-author"><span class="username">user</span></div>
            <div class="post-message">Текст сообщения</div>
        </div>
        """
        posts = self.parser.parse_html(html)

        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["id"], 777)

    def test_save_to_db_saves_all_posts(self):
        posts = self.parser.parse_html(self.fixture_html)
        repo = DatabaseRepository(":memory:")

        try:
            saved = self.parser.save_to_db(posts, repo)

            self.assertEqual(saved, 3)
            self.assertEqual(repo.get_by_id(101)["name"], "ivan_petrov")
            self.assertEqual(len(repo.get_by_name("python_guru")), 1)
        finally:
            repo.close()

    def test_parse_page_downloads_page_and_parses_it(self):
        response = Mock()
        response.text = self.fixture_html
        response.raise_for_status = Mock()

        with patch("src.parser.requests.get", return_value=response) as mock_get:
            posts = self.parser.parse_page("https://forum.example.com/topic/42")

        self.assertEqual(len(posts), 3)
        mock_get.assert_called_once()

        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "https://forum.example.com/topic/42")
        self.assertIn("User-Agent", kwargs["headers"])

    def test_parse_pages_follows_next_link(self):
        page_two_html = (FIXTURES_DIR / "forum_page_2.html").read_text(
            encoding="utf-8"
        )
        responses = {
            "https://forum.example.com/topic/42": self._make_response(
                self.fixture_html
            ),
            "https://forum.example.com/topic/42?page=2": self._make_response(
                page_two_html
            ),
        }

        def fake_get(url, **kwargs):
            return responses[url]

        with patch("src.parser.requests.get", side_effect=fake_get) as mock_get:
            posts = self.parser.parse_pages(
                "https://forum.example.com/topic/42"
            )

        self.assertEqual(
            [post["id"] for post in posts],
            [101, 102, 103, 104],
        )
        self.assertEqual(mock_get.call_count, 2)

    def test_parse_pages_respects_max_pages(self):
        response = self._make_response(self.fixture_html)

        with patch("src.parser.requests.get", return_value=response) as mock_get:
            posts = self.parser.parse_pages(
                "https://forum.example.com/topic/42", max_pages=1
            )

        self.assertEqual(len(posts), 3)
        self.assertEqual(mock_get.call_count, 1)

    def test_parse_pages_stops_without_next_link(self):
        page_two_html = (FIXTURES_DIR / "forum_page_2.html").read_text(
            encoding="utf-8"
        )
        response = self._make_response(page_two_html)

        with patch("src.parser.requests.get", return_value=response) as mock_get:
            posts = self.parser.parse_pages(
                "https://forum.example.com/topic/42?page=2"
            )

        self.assertEqual([post["id"] for post in posts], [104])
        self.assertEqual(mock_get.call_count, 1)

    def test_parse_pages_does_not_follow_same_url_twice(self):
        html = """
        <article class="post" data-post-id="1">
            <div class="post-author"><span class="username">user</span></div>
            <div class="post-message">Текст сообщения</div>
        </article>
        <a class="next" href="/topic/42?page=1">Следующая страница</a>
        """
        response = self._make_response(html)

        with patch("src.parser.requests.get", return_value=response) as mock_get:
            posts = self.parser.parse_pages(
                "https://forum.example.com/topic/42?page=1", max_pages=10
            )

        self.assertEqual(len(posts), 1)
        self.assertEqual(mock_get.call_count, 1)


if __name__ == "__main__":
    unittest.main()
