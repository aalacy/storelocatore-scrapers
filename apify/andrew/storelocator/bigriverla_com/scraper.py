import csv
import os
from selenium import webdriver
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    driver = webdriver.Chrome(f'{os.path.dirname(os.path.abspath(__file__))}/chromedriver')
    driver.get('https://www.bigriverla.com/')
    store_els = driver.find_elements_by_css_selector('ul#menu-big-river-main-menu > li:nth-child(3) > ul > li > a')
    store_urls = [store_el.get_attribute('href') for store_el in store_els]
    import pdb; pdb.set_trace()
    return [["safegraph.com", "SafeGraph", "1543 Mission St.", "San Francisco", "CA", "94103", "US", "<MISSING>", "(415) 966-1152", "Office", 37.773500, -122.417831, "mon-fri 9am-5pm"]]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()