import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
from pysel.items import ProductItem
import sys
sys.path.append("../..")
import pysel.util as util

class MySpider(scrapy.Spider):
    name = 'example'
    allowed_domains = ['books.toscrape.com']
    page_count = 0

    def __init__(self, *args, **kwargs):
        chromedriver_autoinstaller.install()
        self.driver = webdriver.Chrome()
        super(MySpider, self).__init__(*args, **kwargs)
        self.start_urls = util.get_links(self.driver, 'https://books.toscrape.com')

    def parse(self, response):
        self.driver.get(response.url)

            # Let's look for the 'next' button first
        self.page_count += 1  # Increment the page_count every time the parse method is called

        # Check if the limit is reached
        if self.page_count >= 5:
            self.logger.info('Reached the maximum limit of pages. Stopping further scraping.')
            return

        eles = util.filter_elements_without_children(self.driver, "//li", None, ["product_pod"])
        for ele in eles:
            print(ele.get_attribute('outerHTML'))
        for ele in eles:
            name_element = util.get_element(self.driver, ".//h3", ele, 1, [""])
            price_element = util.get_element(self.driver, ".//p", ele, 0, ["price_color"])
            product_item = ProductItem()
            product_item['name'] = name_element.text
            product_item['price'] = price_element.text
            yield product_item

        # next_page = util.get_element(self.driver, "//li", None, 1, [">next<"])
        # if next_page:
        #     print("Next page link found!")
        #     next_page_url = util.get_element(self.driver, ".//a", next_page, 0, ["next"])
        #     url = next_page_url.get_attribute('href')
        #     if next_page_url:
        #         yield scrapy.Request(url, callback=self.parse)
        # else:
        #     print("Next page link not found!")

    def closed(self, reason):
        self.driver.quit()