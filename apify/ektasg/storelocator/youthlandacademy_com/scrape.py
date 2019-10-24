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

#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)
#driver2 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver2 = webdriver.Chrome("chromedriver", options=options)


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
    driver.get("https://www.youthlandacademy.com/location")
    time.sleep(10)
    page_url = "https://www.youthlandacademy.com/location"
    text = driver.find_element_by_xpath("/html/body/script[2]").get_attribute('innerText')
    text_1 = text.split('MapifyPro.Google(center')[1].split(', zoom,')[1]
    text_1 = text_1.split(', map_instance,')[0]
    req_json = json.loads(text_1)
    count =0
    for i in range(len(req_json)):
        name = req_json[i]['post_title']
        street1 = req_json[i]['tooltip_content'].split('<br />')[1]
        state = req_json[i]['tooltip_content'].split('<br />')[2].split('</p>')[0].split(',')[1].split(" ")[1]
        zipcode = req_json[i]['pin_zip']
        city = req_json[i]['pin_city']
        lat = req_json[i]['google_coords'][0]
        lng = req_json[i]['google_coords'][1]
        country = req_json[i]['tooltip_content'].split('<br />')[2].split('</p>')[0].split(',')[2]
        phone = req_json[i]['tooltip_content'].split('<br />')[2].split('</i>')[1]
        store_id = req_json[i]['ID']
        try:
            hour = req_json[i]['tooltip_content'].split('<br />')[4].replace('</p>', '').replace('\n', '').replace(
                '<strong>', '').replace('</strong>', '')
        except:
            pass

        data.append([
            'www.youthlandacademy.com',
            page_url,
            name,
            street1,
            city,
            state,
            zipcode,
            country,
            store_id,
            phone,
            '<MISSING>',
            lat,
            lng,
            hour
        ])
        count+=1
        print(count)

    time.sleep(3)
    driver.quit()
    driver2.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)

scrape()





