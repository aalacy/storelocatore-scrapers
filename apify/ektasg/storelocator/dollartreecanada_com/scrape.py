import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)
#driver2 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver2 = webdriver.Chrome("chromedriver", options=options)
#driver3 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver3 = webdriver.Chrome("chromedriver", options=options)
#driver4 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver4 = webdriver.Chrome("chromedriver", options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)



def fetch_data():
    # Your scraper here
    count=0
    data=[]
    driver.get("https://locations.dollartreecanada.com/")
    time.sleep(10)
    stores = driver.find_elements_by_css_selector('div.details > p:nth-child(5) > a')
    name = [stores[i].get_attribute('href') for i in range(0, len(stores))]
    for i in range(0,len(name)):
            driver2.get(name[i])
            page_url = name[i]
            #print(page_url)
            time.sleep(1)
            stores1 = driver2.find_elements_by_css_selector('div.details > p:nth-child(4) > a')
            name_sub = [stores1[m].get_attribute('href') for m in range(0, len(stores1))]
            for j in range(0,len(name_sub)):
                    driver3.get(name_sub[j])
                    page_url = name_sub[j]
                    #print(page_url)
                    time.sleep(1)
                    store_view_details = driver3.find_elements_by_css_selector('div.details > p > a')
                    store_view_details_lnks = [store_view_details[n].get_attribute('href') for n in range(0, len(store_view_details))]
                    for k in range(0,len(store_view_details_lnks)):
                        driver4.get(store_view_details_lnks[k])
                        time.sleep(1)
                        page_url = store_view_details_lnks[k]
                        #print(page_url)
                        location_name = driver4.find_element_by_css_selector('#block-block-3 > h1').text
                        location_name = location_name.split("Welcome to ")[1]
                        store_id = driver4.find_element_by_css_selector('div.detailsPad > div:nth-child(2) > span:nth-child(1)').text
                        store_id = store_id.split("#")[1]
                        street_addr = driver4.find_element_by_xpath("//span[contains(@itemprop, 'streetAddress')]").text
                        city = driver4.find_element_by_xpath("//span[contains(@itemprop, 'addressLocality')]").text
                        state = driver4.find_element_by_xpath("//span[contains(@itemprop, 'addressRegion')]").text
                        zipcode = driver4.find_element_by_xpath("//span[contains(@itemprop, 'postalCode')]").text
                        country = driver4.find_element_by_xpath("//span[contains(@itemprop, 'addressCountry')]").text
                        phone = driver4.find_element_by_xpath("//a[contains(@itemprop, 'telephone')]").text
                        hours_of_op = driver4.find_element_by_css_selector('div.hours').text.replace("\n", " ")
                        latitude = driver4.find_element_by_xpath("//meta[contains(@property, 'place:location:latitude')]").get_attribute('content')
                        longitude = driver4.find_element_by_xpath("//meta[contains(@property, 'place:location:longitude')]").get_attribute('content')
                        data.append([
                            'https://www.dollartreecanada.com/',
                            page_url,
                            location_name,
                            street_addr,
                            city,
                            state,
                            zipcode,
                            country,
                            store_id,
                            phone,
                            '<MISSING>',
                            latitude,
                            longitude,
                            hours_of_op
                        ])
                        count = count + 1
                        print(count)

    time.sleep(3)
    driver.quit()
    driver2.quit()
    driver3.quit()
    driver4.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
