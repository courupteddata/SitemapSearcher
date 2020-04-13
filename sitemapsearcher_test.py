import unittest
import sitemapsearcher


class ParsingRobotsTXT(unittest.TestCase):
    def test_base_functionality_with_https_and_www(self):
        searcher = sitemapsearcher.SitemapSearcher()
        searcher.search("https://www.google.com", [])
        self.assertEqual(searcher._robots_found_sitemap, {"https://www.google.com/sitemap.xml"})

    def test_base_functionality_with_https(self):
        searcher = sitemapsearcher.SitemapSearcher()
        searcher.search("https://google.com", [])
        self.assertEqual(searcher._robots_found_sitemap, {"https://www.google.com/sitemap.xml"})

    def test_base_functionality_with_http_and_www(self):
        searcher = sitemapsearcher.SitemapSearcher()
        searcher.search("http://www.google.com", [])
        self.assertEqual(searcher._robots_found_sitemap, {"https://www.google.com/sitemap.xml"})

    def test_base_functionality_with_http(self):
        searcher = sitemapsearcher.SitemapSearcher()
        searcher.search("http://google.com", [])
        self.assertEqual(searcher._robots_found_sitemap, {"https://www.google.com/sitemap.xml"})

    def test_base_functionality_gzipped(self):
        searcher = sitemapsearcher.SitemapSearcher()
        searcher.search("https://www.yahoo.com", [])
        self.assertGreaterEqual(len(searcher._robots_found_sitemap), 5)


if __name__ == '__main__':
    unittest.main()
