import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def write_output(data):
    with open('data.csv', mode='w') as output_file:
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
    url = 'http://www.gvgrocery.com/locations/'
    driver = get_driver()
    driver.get(url)
    time.sleep(2)
    button = driver.find_element_by_id('store_locator_get_all_stores')
    button.click()
    time.sleep(5)
    maindiv = driver.find_element_by_id('store_locator_result_list')

    repo_list = maindiv.find_elements_by_class_name('store_locator_result_list_item')



    cleanr = re.compile('<.*?>')
    pattern = re.compile(r'\s\s+')
    print(len(repo_list))

    for n in range(0,len(repo_list)):

        title = repo_list[n].find_element_by_class_name('store_locator_name').text
        start = title.find("#")
        store = title[start+1:len(title)]
        try:
            street = repo_list[n].find_element_by_class_name('store_locator_street').text
        except:
            street = "<MISSING>"
        try:
            city = repo_list[n].find_element_by_class_name('store_locator_city').text
        except:
            city = "<MISSING>"
        try:
            pcode = repo_list[n].find_element_by_class_name('store_locator_zip').text
        except:
            pcode = "<MISSING>"
        try:
            phone = repo_list[n].find_element_by_class_name('store_locator_tel').text
        except:
            phone = "<MISSING>"
        coord = repo_list[n].find_element_by_class_name('store_locator_actions').find_element_by_tag_name('a').get_attribute('href')
        coord = str(coord)
        if coord == "None":
            lat = "<MISSING>"
            longt = "<MISSING>"
        else:

            start = coord.find("=") +1
            end = coord.find(",", start)
            lat = coord[start+1:end]
            longt = coord[end + 1 :len(coord)]

        city = city.replace(",", "")
        phone = phone.replace("T : ","")


        print(title)
        print(store)
        print(street)
        print(city)
        print(pcode)
        print(phone)
        #print(coord)
        print(lat)
        print(longt)
        print(p)
        print("...........................")
        p += 1
        data.append([
            'http://www.gvgrocery.com',
            'http://www.gvgrocery.com/locations/',
            title,
            street,
            city,
            "<MISSING>",
            pcode,
            'US',
            store,
            phone,
            "<MISSING>",
            lat,
            longt,
            "<MISSING>"
        ])

    return data


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
