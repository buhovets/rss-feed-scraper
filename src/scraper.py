import json
import os
from urllib.parse import urljoin
from requests_html import HTMLSession
from bs4 import BeautifulSoup

from config import logger_config

class WebScraper:
    def __init__(self):
        self.session = HTMLSession()
        self.logger = logger_config()

    def get_soup(self, url: str) -> BeautifulSoup:
        """
        Get and parse the HTML content of a given URL.

        Args:
            url (str): The URL to fetch and parse.

        Returns:
            BeautifulSoup: A BeautifulSoup object containing the parsed HTML content.
        """
        response = self.session.get(url)
        return BeautifulSoup(response.text, 'html.parser')

    def get_links(self, url: str, link_selector: str) -> list[str]:
        """
        Extract and return a list of links found on a webpage based on a CSS selector.

        Args:
            url (str): The URL of the webpage to scrape.
            link_selector (str): The CSS selector used to locate links.

        Returns:
            list[str]: A list of extracted links.
        """
        soup = self.get_soup(url)
        link_elements = soup.select(link_selector)
        
        links = []
        for link_element in link_elements:
            href = link_element.get('href')
            if href:
                href = f"https:{href}" if href.startswith('//') else href
                href = urljoin(url, href) if href.startswith('/') else href
                if 'video' in href:
                    continue
                links.append(href)
                
        self.logger.info(f"Found {len(links)} links")
        return links

    def parse_article(self, url: str, title_selector: str, content_selector: str) -> dict[str, str] | None:
        """
        Parse an article's title and content from a given URL.

        Args:
            url (str): The URL of the article.
            title_selector (str): The CSS selector for locating the article title.
            content_selector (str): The CSS selector for locating the article content.

        Returns:
            dict[str, str] | None: A dictionary containing the title and content of the article,
                or None if parsing fails.
        """
        try:
            article = self.get_soup(url)
            title = article.select_one(title_selector).text
            article_body = article.select_one(content_selector)
            paragraphs = article_body.find_all('p')
            if not paragraphs:
                paragraphs = article_body.find_all('div[data-component="text-block"]')
            content = "\n".join([p.text for p in paragraphs])
            
            self.logger.info(f"Parsing url: {url}")
            self.logger.info(f"Title:\n {title}")
            self.logger.info(f"Content:\n {content}\n\n")

            return {
                "title": title,
                "content": content
            }
        except Exception as e:
            self.logger.error(f"Error parsing article: {url}")
            self.logger.error(e)
            return None

    def scrape_articles(self, url: str, link_selector: str, title_selector: str, content_selector: str) -> list[dict[str, str] | None]:
        """
        Scrape and parse articles from a webpage.

        Args:
            url (str): The URL of the webpage to scrape.
            link_selector (str): The CSS selector for locating article links.
            title_selector (str): The CSS selector for locating article titles.
            content_selector (str): The CSS selector for locating article content.

        Returns:
            List[Dict[str, str]]: A list of dictionaries, where each dictionary contains the title and content
                of an article.
        """
        links = self.get_links(url, link_selector)
        articles = []

        for link in links:
            article_data = self.parse_article(link, title_selector, content_selector)
            if article_data:
                articles.append(article_data)

        return articles

    @staticmethod
    def save_to_json(output_file: str, data: list[dict[str, str]]) -> None:
        """
        Save data to a JSON file.

        Args:
            output_file (str): The name of the output JSON file.
            data (list[dict[str, str]]): The data to be saved.
        """
        with open(output_file, 'w') as file:
            json.dump(data, file, indent=4)