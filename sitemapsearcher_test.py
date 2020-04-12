import unittest
import sitemapsearcher


class ParsingRobotsTXT(unittest.TestCase):
    def test_base_functionality_with_https_and_www(self):
        searcher = sitemapsearcher.SitemapSearcher()
        searcher.search("https://www.google.com", [])
        self.assertEqual(searcher._found_sitemap, {"https://www.google.com/sitemap.xml"})

    def test_base_functionality_with_https(self):
        searcher = sitemapsearcher.SitemapSearcher()
        searcher.search("https://google.com", [])
        self.assertEqual(searcher._found_sitemap, {"https://www.google.com/sitemap.xml"})

    def test_base_functionality_with_http(self):
        searcher = sitemapsearcher.SitemapSearcher()
        searcher.search("http://google.com", [])
        self.assertEqual(searcher._found_sitemap, {"https://www.google.com/sitemap.xml"})


if __name__ == '__main__':
    unittest.main()
