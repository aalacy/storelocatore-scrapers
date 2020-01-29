import requests
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import pandas as pd
from selenium.webdriver.support.ui import Select
import csv
import time
import re


def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument(
        "user-agent= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36")
    return webdriver.Chrome('chromedriver', options=options)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Begin scraper

    base_url = "https://www.sprouts.com"
    location_url = "https://www.sprouts.com/stores/"
    locs = []
    streets = []
    states = []
    cities = []
    types = []
    phones = []
    zips = []
    longs = []
    lats = []
    timing = []
    ids = []
    pages_url = []
    urls = []
    res = []

    driver = get_driver()
    driver_page = get_driver()
    driver_url = get_driver()
    time.sleep(3)
    driver.get(location_url)
    res=[]
    all_states = driver.find_element_by_id("wpv-view-layout-4479").find_elements_by_tag_name("a")
    #print(len(all_states))    
    for sta in all_states:
        driver_page.get(sta.get_attribute('href'))
        #print(sta.get_attribute('href'))
        sts= driver_page.find_element_by_id("wpv-view-layout-4514").find_elements_by_tag_name("div")
        del sts[0]
        #print(len(sts))
        for st in sts:
          if "Coming Soon" in st.text:
                   print(st.find_element_by_tag_name('a').text)
          else:
               res.append(st.find_element_by_tag_name('a').get_attribute('href'))
    print(len(res))
    for u in res:
        driver_url.get(u)
        print(u)
        locs.append(driver_url.find_element_by_xpath('/html/body/main/article/div/div/div[2]/div[1]/div/h1').text.replace('â€“',''))
        addr=driver_url.find_element_by_class_name("store-address").find_element_by_tag_name('a').text
        streets.append(
            addr.split(
                '\n')[0])
        cities.append(
            addr.split(
                '\n')[1].split(',')[0])
        states.append(
            addr.split(
                ',')[-1].split(' ')[1])
        zips.append(
            addr.split(
                ',')[-1].split(' ')[2])
        """except:
          streets.append(
            driver_url.find_element_by_xpath('/html/body/main/article/div/div/div[1]/div[1]/div/p[2]/a').text.split(
                '\n')[0])
          cities.append(
            driver_url.find_element_by_xpath('/html/body/main/article/div/div/div[1]/div[1]/div/p[2]/a').text.split(
                '\n')[1].split(',')[0])
          states.append(
            driver_url.find_element_by_xpath('/html/body/main/article/div/div/div[1]/div[1]/div/p[2]/a').text.split(
                ',')[-1].split(' ')[1])
          zips.append(
            driver_url.find_element_by_xpath('/html/body/main/article/div/div/div[1]/div[1]/div/p[2]/a').text.split(
                ',')[-1].split(' ')[2])"""
        try:
            ids.append(
                driver_url.find_element_by_xpath('/html/body/main/article/div/div/div[2]/div[1]/div/p[1]').text.split(
                    '#')[1])
        except:
            ids.append("<MISSING>")
        try:
            phones.append(
                driver_url.find_element_by_xpath("/html/body/main/article/div/div/div[2]/div[1]/div/p[3]/a").text)
        except:
            phones.append("<MISSING>")
        types.append(
            driver_url.find_element_by_xpath("/html/body/main/article/div/section[1]/div/div/div[1]/ul").text.replace(
                '\n', ' '))
        lats.append(driver_url.find_element_by_xpath("/html/body/main/article/div/div/div[1]").get_attribute('lat'))
        longs.append(driver_url.find_element_by_xpath("/html/body/main/article/div/div/div[1]").get_attribute('lon'))
        try:
            timing.append(
                driver_url.find_element_by_xpath("/html/body/main/article/div/div/div[2]/div[1]/div/p[4]/span[1]").text)
        except:
            timing.append("<MISSING>")

    return_main_object = []
    for l in range(len(locs)):
        row = []
        row.append(base_url)
        row.append(locs[l] if locs[l] else "<MISSING>")
        row.append(streets[l] if streets[l] else "<MISSING>")
        row.append(cities[l] if cities[l] else "<MISSING>")
        row.append(states[l] if states[l] else "<MISSING>")
        row.append(zips[l] if zips[l] else "<MISSING>")
        row.append("US")
        row.append(ids[l] if ids[l] else "<MISSING>")
        row.append(phones[l] if phones[l] else "<MISSING>")
        row.append(types[l] if types[l] else "<MISSING>")
        row.append(lats[l] if lats[l] else "<MISSING>")
        row.append(longs[l] if longs[l] else "<MISSING>")
        row.append(timing[l] if timing[l] else "<MISSING>")
        row.append(res[l] if res[l] else "<MISSING>")

        return_main_object.append(row)

    # End scraper
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
