import unittest
import sitemapsearcher


class ParsingRobotsTXT(unittest.TestCase):
    def test_base_functionality_with_https_and_www(self):
        searcher = sitemapsearcher.SitemapSearcher()
        self.assertEqual(searcher._parse_robots_txt("https://www.google.com"), {"https://www.google.com/sitemap.xml"})

    def test_base_functionality_with_https(self):
        searcher = sitemapsearcher.SitemapSearcher()
        self.assertEqual(searcher._parse_robots_txt("https://google.com"), {"https://www.google.com/sitemap.xml"})

    def test_base_functionality_with_http_and_www(self):
        searcher = sitemapsearcher.SitemapSearcher()
        self.assertEqual(searcher._parse_robots_txt("http://www.google.com"), {"https://www.google.com/sitemap.xml"})

    def test_base_functionality_with_http(self):
        searcher = sitemapsearcher.SitemapSearcher()
        self.assertEqual(searcher._parse_robots_txt("http://google.com"), {"https://www.google.com/sitemap.xml"})

    def test_base_functionality_gzipped(self):
        searcher = sitemapsearcher.SitemapSearcher()
        self.assertGreaterEqual(len(searcher._parse_robots_txt("https://www.yahoo.com")), 5)


class LoadSitemapData(unittest.TestCase):
    def test_normal_sitemap(self):
        searcher = sitemapsearcher.SitemapSearcher()
        data = searcher._load_sitemap_data("https://www.google.com/sitemap.xml")
        self.assertGreaterEqual(len(data), 1000)
        self.assertTrue(b"<sitemapindex" in data)

    def test_gzipped_data(self):
        searcher = sitemapsearcher.SitemapSearcher()
        data = searcher._load_sitemap_data("https://www.yahoo.com/news/sitemaps/news-sitemap_index_US_en-US.xml.gz")
        self.assertGreaterEqual(len(data), 1000)
        self.assertTrue(b"<sitemapindex" in data)

if __name__ == '__main__':
    unittest.main()
