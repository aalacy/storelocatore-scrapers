# Import libraries
import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select


def write_output(data):
    with open('data.csv', mode='w', encoding='utf-8') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain","page_url",  "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    chrome_path = '/Users/Dell/local/chromedriver'
    #return webdriver.Chrome(chrome_path, chrome_options=options)
    return webdriver.Chrome('chromedriver', chrome_options=options)


def fetch_data():
    # Your scraper here
    data = []
    p = 1
    url = 'https://hymiler.com/locations/hy-miler-2224-townsend-road'
    driver = get_driver()
    driver.get(url)
    time.sleep(2)
    mainselect = driver.find_element_by_xpath('/html/body/div[2]/div/div[2]/div/div/div[2]/div[2]/div/div/div/select')
    poption = mainselect.find_elements_by_tag_name('option')
    print(len(poption))
    locs = []
    titles = []

    for n in range(1, len(poption)):
        link = poption[n].get_attribute('value')
        link = "https://hymiler.com" + link
        locs.append(link)
        titles.append(poption[n].text)
    locs.append('https://hymiler.com/locations/hy-miler-2224-townsend-road')
    titles.append('Hy-Miler #2224, Townsend Road')

    for n in range(0, len(locs)):
        link = locs[n]
        title = titles[n]

        print(link)
        driver1 = get_driver()
        driver1.get(link)
        time.sleep(2)
        start = title.find("#") + 1
        end = title.find(",", start)
        store = title[start:end]
        maindiv = driver1.find_element_by_class_name('locationaddress')
        detail = maindiv.text
        detail = detail.replace("\n","|")
        print(detail)
        start = detail.find("|")
        street = detail[0:start]
        start = start + 1
        end = detail.find(",", start)
        city = detail[start:end]
        start = end + 1
        end = detail.find("|", start)
        state = detail[start:end]
        start = detail.find("States",end)
        start = detail.find(" ",start) + 1
        end = detail.find("|", start)
        pcode = detail[start:end]
        start = end + 1
        phone = detail[start:len(detail)]

        detail = str(driver1.page_source)
        start = detail.find('"coordinates"')
        start = detail.find('[', start)+ 1
        end = detail.find(",", start)
        longt = detail[start:end]
        start = end + 1
        end = detail.find(']',start)
        lat = detail[start:end]

        detail = driver1.find_element_by_xpath('//*[@id="locationsearch"]/div[2]/span[2]')
        detail = detail.text
        if detail.find("Open 24 hours") > -1:
            hours = "Open 24 hours"
        else:
            hours = "<MISSING>"
        lat = lat[0:8]
        longt = longt[0:8]
        title = title.replace(",", "")

        print(title)
        print(store)
        print(street)
        print(city)
        print(state)
        print(pcode)
        print(phone)
        print(lat)
        print(longt)
        print(hours)
        print(p)
        print(".................")
        p += 1
        driver1.quit()
        data.append([
            'https://hymiler.com',
            link,
            title,
            street,
            city,
            state,
            pcode,
            'US',
            store,
            phone,
            "<MISSING>",
            lat,
            longt,
            hours
        ])

    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
