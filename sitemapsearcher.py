"""
MIT License

Copyright (c) 2020 Nathan
Original available at https://github.com/courupteddata/SitemapSearcher

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This is a class that handles extracting the url locations of all the sitemap entries and then doing basic percentage
matching for certain keywords.
"""

import urllib.parse
import urllib.request
import urllib.robotparser
import urllib.error
import gzip
import defusedxml.ElementTree
import xml.etree.ElementTree
from typing import List, Dict, Set, Union

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
        self._robots_found_sitemap = set()
        self._all_sitemaps = set()

    def search(self, base_url: str, key_word_list: List[str], case_insensitive=True) -> Dict[str, float]:
        """
        Note that search is NOT thread safe, don't call search from many threads, instead instantiate a searcher per
        thread.
        :param base_url: A base url like "https://www.google.com"
        :param key_word_list: A list of strings to search though
        :param case_insensitive: Whether the key_word_list is case insensitive
        :return: A dictionary that contains the original keyword and then a percent of the url entries that matched
        """
        self._robots_found_sitemap = self._parse_robots_txt(base_url)

        # Add sitemap and sitemap index defaults if no sitemap found
        if len(self._robots_found_sitemap) == 0:
            self._all_sitemaps = {self._join_url(base_url, SITEMAP_XML), self._join_url(base_url, SITEMAP_INDEX_XML)}
        else:
            self._all_sitemaps = self._robots_found_sitemap

        local_cache = {}

        for sitemap_url in self._all_sitemaps:
            self._handle(sitemap_url, local_cache)

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

    def _handle(self, sitemap_url: str, local_cache: dict):
        website_data = self._load_sitemap_data(sitemap_url)

        if self._is_sitemap_index(website_data):
            print("sitemap_index", sitemap_url, website_data)
            for new_sitemap_url in self._handle_sitemap_index(website_data):
                self._handle(new_sitemap_url, local_cache)
        else:
            print("sitemap", sitemap_url, website_data)
            self._handle_sitemap(website_data)

    @staticmethod
    def _handle_sitemap(sitemap_data: str) -> Set[str]:
        return set()

    @staticmethod
    def _handle_sitemap_index(sitemap_data: str) -> Set[str]:
        return set()

    @staticmethod
    def _is_sitemap_index(sitemap_data) -> bool:
        """
        Basic check to determine if the given sitemap is actually an index
        :param sitemap_data:
        :return: True if it is a suspected sitemapindex otherwise false
        """
        return b"sitemapindex" in sitemap_data

    def _extract_sitemap_entries(self, sitemap_url: str):  # -> List[str]:
        pass
        # loaded_xml = defusedxml.ElementTree.fromstring(urllib.request.urlopen(sitemap).read())
        # Parsing if this is a index
        # for item in loaded_xml.findall("{*}sitemap"):
        #     print(defusedxml.ElementTree.tostring(item).decode())

    @staticmethod
    def _load_sitemap_data(sitemap_url) -> Union[str, None]:
        """
        This function handle downloading and the possible decompressing of the sitemap data.
        :param sitemap_url: The url to load
        :return: None if an error happened or a byte string containing the data.
        """
        try:
            website_data = urllib.request.urlopen(sitemap_url).read()
        except (urllib.error.ContentTooShortError, urllib.error.HTTPError, urllib.error.ContentTooShortError) as e:
            print(f"Failed to load given sitemap url. {sitemap_url}. {e.reason()}")
            return None

        if ".gz" in sitemap_url.split("/")[-1]:
            try:
                website_data = gzip.decompress(website_data)
            except gzip.BadGzipFile as e:
                print(f"Invalid sitemap that was marked as gzipped, skipping. {sitemap_url}. {e}")
                return None
        return website_data
