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
from typing import List, Dict, Set, Union

# Some constants
SITEMAP_INDEX_XML = "sitemap_index.xml"
SITEMAP_XML = "sitemap.xml"
ROBOTS_TXT = "robots.txt"


class SitemapSearcher:
    def __init__(self, href_lang=("en-us", "en"), cache_enabled=False):
        """
        Creates the sitemap searcher and then run search on a website with
        :param href_lang: defaults to ("en-us", "en") if it's set to None then just loc entry or x-default is used
        :param cache_enabled: Whether to store the cached lookup after parsing sitemap, can enable this if multiple
                              searches will be happening on the same base_website
        """
        self._href_lang = href_lang
        self._cache_enabled = cache_enabled
        self._cache = dict()

    def search(self, base_url: str, key_word_list: List[str], case_insensitive=True) -> Dict[str, float]:
        """
        Note that search is NOT thread safe, don't call search from many threads, instead instantiate a searcher per
        thread.
        :param base_url: A base url like "https://www.google.com"
        :param key_word_list: A list of strings to search though
        :param case_insensitive: Whether the key_word_list is case insensitive
        :return: A dictionary that contains the original keyword and then a percent of the url entries that matched
        """
        robots_found_sitemap = self._parse_robots_txt(base_url)

        # Add sitemap and sitemap index defaults if no sitemap found
        if len(robots_found_sitemap) == 0:
            all_sitemaps = {self._join_url(base_url, SITEMAP_XML), self._join_url(base_url, SITEMAP_INDEX_XML)}
        else:
            all_sitemaps = robots_found_sitemap

        local_cache = set()

        for sitemap_url in all_sitemaps:
            self._handle(sitemap_url, local_cache)

        results = dict()

        for key_word in key_word_list:
            if case_insensitive:
                key_word = key_word.lower()
            results[key_word] = 0

        if not len(local_cache) > 0:
            return results

        for item in local_cache:
            if case_insensitive:
                item = item.lower()
            item = "/".join(item.split("/")[3:])
            for key in results:
                if key in item:
                    results[key] += 1

        for key in results:
            results[key] = results[key] / len(local_cache)

        return results

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
        """
        Joins two parts, the base url and the extra part
        :param base_url: The base url is something like https://google.com
        :param extra_part: The extra part is something like robots.txt
        :return: The valid url that is combined of the two
        """
        return urllib.parse.urljoin(base_url, extra_part)

    def _handle(self, sitemap_url: str, local_cache: set):
        """
        This function handles loading the given sitemap url and then adding information to the local cache
        :param sitemap_url: The sitemap url to load
        :param local_cache: The local cache to store information in
        :return: None
        """
        website_data = self._load_sitemap_data(sitemap_url)

        if website_data is None:
            return

        if self._is_sitemap_index(website_data):
            for new_sitemap_url in self._handle_sitemap_index(website_data):
                self._handle(new_sitemap_url, local_cache)
        else:
            local_cache.update(self._handle_sitemap(website_data))

    def _handle_sitemap(self, sitemap_data: bytes) -> Set[str]:
        try:
            sitemap_xml = defusedxml.ElementTree.fromstring(sitemap_data)
        except defusedxml.ElementTree.ParseError as e:
            print(f"Failed to parse sitemap. {e}")
            return set()

        found_locs = set()

        for item in sitemap_xml.findall("{*}url"):
            # Grab required loc first
            loc = item.find("{*}loc")
            if loc is not None:
                loc = loc.text

            default_test = item.find("*/[@hreflang='x-default']")
            if default_test is not None:
                loc = default_test.attrib["href"]

            if self._href_lang is not None:
                for lang in self._href_lang:
                    # Check if there is multiple languages and select the correct one
                    language_specific_loc = item.find(f"*/[@hreflang='{lang}']")
                    if language_specific_loc is not None:
                        loc = language_specific_loc.attrib["href"]
                        break

            if loc is not None:
                found_locs.add(loc)
        return found_locs

    @staticmethod
    def _handle_sitemap_index(sitemap_data: bytes) -> Set[str]:
        """
        Handles extracting all of the actual sitemap urls
        :param sitemap_data: The bytes that are downloaded sitemap index
        :return: a set of sitemap urls as strings
        """
        try:
            sitemap_xml = defusedxml.ElementTree.fromstring(sitemap_data)
        except defusedxml.ElementTree.ParseError as e:
            print(f"Failed to parse sitemap index. {e}")
            return set()

        sitemap_index_entries = set()

        for item in sitemap_xml.findall("{*}sitemap/{*}loc"):
            sitemap_index_entries.add(item.text)

        return sitemap_index_entries

    @staticmethod
    def _is_sitemap_index(sitemap_data: bytes) -> bool:
        """
        Basic check to determine if the given sitemap is actually an index
        :param sitemap_data:
        :return: True if it is a suspected sitemapindex otherwise false
        """
        return b"<sitemapindex" in sitemap_data

    @staticmethod
    def _load_sitemap_data(sitemap_url: str) -> Union[bytes, None]:
        """
        This function handle downloading and the possible decompressing of the sitemap data.
        :param sitemap_url: The url to load
        :return: None if an error happened or a byte string containing the data.
        """
        try:
            website_data = urllib.request.urlopen(sitemap_url).read()
        except (urllib.error.ContentTooShortError, urllib.error.HTTPError, urllib.error.ContentTooShortError) as e:
            print(f"Failed to load given sitemap url. {sitemap_url}. {e}")
            return None

        if ".gz" in sitemap_url.split("/")[-1]:
            try:
                website_data = gzip.decompress(website_data)
            except gzip.BadGzipFile as e:
                print(f"Invalid sitemap that was marked as gzipped, skipping. {sitemap_url}. {e}")
                return None
        return website_data


if __name__ == '__main__':
    print(SitemapSearcher().search("https://google.com", ["gmail", "search", "company", "business"]))
