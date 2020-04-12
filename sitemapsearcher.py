import urllib.request, urllib.robotparser, urllib.parse
from typing import List, Dict, Set

# Some constants
SITEMAP_INDEX_XML = "sitemap_index.xml"
SITEMAP_XML = "sitemap.xml"
ROBOTS_TXT = "robots.txt"


class SitemapSearcher:
    def __init__(self, href_lang="en-us", cache_enabled=False):
        """
        Creates the sitemap searcher and then run search on a website with
        :param href_lang: default to "en-us" if it's set to None then all <xhtml:link > entries are added if they exist
        :param cache_enabled: Whether to store the cached lookup after parsing sitemap, can enable this if multiple searched
                              will be happening on the same base_website
        """
        self._href_lang = href_lang
        self._cache_enabled = cache_enabled
        self._cache = dict()

        # Some most recent fields used for testing
        self._found_sitemap = set()

    def search(self, base_url: str, key_word_list: List[str], case_insensitive=True) -> Dict[str, float]:
        """
        :param base_url: A base url like "https://www.google.com"
        :param key_word_list: A list of strings to search though
        :param case_insensitive: Whether the key_word_list is case insensitive
        :return: A dictionary that contains the original keyword and then a percent of the url entries that matched
        """
        self._found_sitemap = self._parse_robots_txt(base_url)

        return {"WIP": 1.0}

    @staticmethod
    def _parse_robots_txt(base_url: str) -> Set[str]:
        """
        Parses robots.txt file for site map entries
        :param base_url: A base url like "https://www.google.com"
        :return:
        """
        robots_txt_url = SitemapSearcher._join_url(base_url, ROBOTS_TXT)
        robot_parser = urllib.robotparser.RobotFileParser(robots_txt_url)
        robot_parser.read()
        if (site_map := robot_parser.site_maps()) is None:
            return set()
        else:
            return set(site_map)

    @staticmethod
    def _join_url(base_url: str, extra_part: str) -> str:
        return urllib.parse.urljoin(base_url, extra_part)
