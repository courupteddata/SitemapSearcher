# SitemapSearcher
Created in response to this https://www.reddit.com/r/programmingrequests/comments/fvfihm/mass_sitemap_scraper_and_analyzer_possible/ request.

This was written with Python3.8.


Notes:

First search a sites robots.txt and extract "Sitemap: http://www.example.com/sitemap.xml" entries and also try default locations "http://www.example.com/sitemap.xml" and "http://www.example.com/sitemap_index.xml"

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