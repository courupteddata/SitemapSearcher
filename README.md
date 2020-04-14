<p>
  <a href="https://github.com/courupteddata/SitemapSearcher"><img alt="StringBooleanExpression status" src="https://github.com/courupteddata/SitemapSearcher/workflows/SitemapSearcher-unit-tests/badge.svg"></a>
</p>

# SitemapSearcher
Created in response to this https://www.reddit.com/r/programmingrequests/comments/fvfihm/mass_sitemap_scraper_and_analyzer_possible/ request.

## How to use
After downloading the project run:
```
pip3 install -r requirements.txt
```
Now it should be as simple as importing sitemapsearcher and adding something like this:
```pythonstub
import sitemapsearcher
if __name__ == '__main__':
    searcher = sitemapsearcher.SitemapSearcher()
    print(searcher.search("https://google.com", ["gmail", "search", "company", "business"]))
```

## Dependencies
- Python >= 3.8
- defusedxml python library (to handle parsing xml in a safe manner)

## Extra Features
If it is desired there is an option to enable a local cache that allows reusing the same found links for multiple times for different searches.

Note: It should NOT be used if repeated lookups are not desired since this will waste memory.

For example:
```pythonstub
import sitemapsearcher
if __name__ == '__main__':
    searcher = sitemapsearcher.SitemapSearcher(cache_enabled=True)
    print(searcher.search("https://google.com", ["gmail", "search", "company", "business"]))
    print(searcher.search("https://google.com", ["gmail", "search", "company", "business", "google", "else"]))
```
Also this library attempts to filter based on basic hreflang which can be modified with href_lang tuple specified in the constructor.


## What's happening under the hood:

First search a sites robots.txt and extract "Sitemap: http://www.example.com/sitemap.xml" entries and also try default locations "http://www.example.com/sitemap.xml" and "http://www.example.com/sitemap_index.xml" if no entries in "robots.txt"

Two types, sitemapindex and sitemap.

sitemapindex format: (links to other sitemaps)
````xml
<sitemapindex> 
 <sitemap>
  <loc>https://www.google.com/gmail/sitemap.xml</loc>
 </sitemap>
 <sitemap>
  <loc>https://www.google.com/forms/sitemap.xml</loc>
 </sitemap>
</sitemapindex>
````

sitemap format: (is the sitemap, can also be a text list of sites)
````xml
<urlset>
 <url>
  <loc>https://www.google.com/intl/am/gmail/about/</loc>
  <xhtml:link href="https://www.google.com/gmail/about/" hreflang="x-default" rel="alternate"/>
</url>
</urlset>
````
