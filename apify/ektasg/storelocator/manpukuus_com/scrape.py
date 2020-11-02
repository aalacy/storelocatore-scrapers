import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import json

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--disable-plugins")
options.add_argument("--no-experiments")
options.add_argument("--disk-cache-dir=null")

#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon


def fetch_data():
    data = []
    driver.get("http://www.manpukuus.com/locations/")
    time.sleep(10)
    name = driver.find_element_by_xpath("//script[parent::div[@class='fusion-column-wrapper']]").get_attribute(
        'innerHTML')
    name = name.split('addresses')[1].split('],')[0] + "]"
    name = name[2:]
    name = json.loads(name)
    name = [name[2], name[1], name[3], name[0]]
    li_url = []

    abc = driver.find_elements_by_xpath("//span[@class='fusion-column-inner-bg hover-type-none']//a")
    for j in abc:
        li_url.append(j.get_attribute('href'))
    for i in range(len(li_url)):
        li = []
        driver.get(li_url[i])
        page_url = li_url[i]
        sn = driver.find_element_by_xpath("//h2")
        location_name = sn.get_attribute('textContent')
        info = driver.find_elements_by_xpath("//div//p//span")
        country = 'US'
        latitude = name[i]['latitude']
        longitude = name[i]['longitude']
        street_address = name[i]['infobox_content'].split("<br>")[0]
        city = name[i]['infobox_content'].split("<br>")[1].split(",")[0]
        state = name[i]['infobox_content'].split("<br>")[1].split(",")[1].split(' ')[1]
        phone = name[i]['infobox_content'].split("<br>")[2].split(':')[1]
        zipcode = name[i]['infobox_content'].split("<br>")[1].split(",")[1].split(' ')[2]
        for j in range(len(info)):
            li.append(info[j].get_attribute('textContent'))
        hours_of_operation = li[2:]
        str1 =" "
        str2 = str1.join(hours_of_operation).replace('\\xa', " ")
        try:
            store_id_info= driver.execute_script("return window.OT.Widget")
            store_id = store_id_info['options']['restaurantId']
        except:
            store_id ='<MISSING>'
        data.append([
            'www.manpukuus.com',
            page_url,
            location_name,
            street_address,
            city,
            state,
            zipcode,
            country,
            store_id,
            phone,
            '<MISSING>',
            latitude,
            longitude,
            str2
        ])

    time.sleep(3)
    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()




