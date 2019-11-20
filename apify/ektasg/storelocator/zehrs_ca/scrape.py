import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')
options.add_argument("user-agent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'")

#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)
#driver2 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver2 = webdriver.Chrome("chromedriver", options=options)
#driver3 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver3 = webdriver.Chrome("chromedriver", options=options)


def parse_geo(url):
    try:
        lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    except:
        lon = re.findall(r'\,(-?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)




def fetch_data():

    data = []
    driver.get("https://www.zehrs.ca/store-locator?icta=store-locator")
    time.sleep(15)
    driver.find_element_by_xpath("//button[@title='Zoom out']").click()
    time.sleep(15)

    stores = driver.find_elements_by_xpath("//a[contains(@class,'list-item__details-link')]")
    names = [stores[i].get_attribute("href") for i in range(0, len(stores))]

    for i in range(0, len(names)):
        print (i)
        driver2.get(names[i])
        time.sleep(5)
        page_url = names[i]
        store_opening_hours =driver2.find_element_by_xpath("(//div[contains(@class,'hours-section__weekly-hours-group hours-')]) ").get_attribute("textContent").replace('\t','').replace('\n','')
        phone_no =driver2.find_element_by_xpath("(//p[contains(@class,'store-information__content')]) ").get_attribute("textContent").replace('\t','').replace('\n','').replace("'",'')
        store_id = names[i].split("storeId=")[1]
        geomap = driver2.find_element_by_css_selector('a.address-and-cta__get-directions-link').get_attribute('href')
        driver3.get(geomap)
        time.sleep(5)
        lat, lon = parse_geo(driver3.current_url)
        store_address =driver.find_element_by_xpath("(//div[contains(@class,'list-item__button-details')])["+str(i+1)+"]/p[contains(@class,'list-item__address address')] ").get_attribute("textContent")
        street_addr =driver.find_element_by_xpath("(//span[contains(@class,'address__street-address')])["+str(i+1)+"] ").get_attribute("textContent")
        store_name =driver.find_element_by_xpath("(//h1[contains(@class,'list-item__store-name')])["+str(i+1)+"] ").get_attribute("textContent")
        city_postal_address =driver.find_element_by_xpath("(//span[contains(@class,'address__city-postal-code')])["+str(i+1)+"] ").get_attribute("textContent")

        data.append([
             '"https://www.zehrs.ca/',
              page_url,
              store_name,
              street_addr,
              city_postal_address.split(",")[0],
              city_postal_address.split(",")[1].split(" ")[1],
              city_postal_address.split(" ")[-2]+" "+ city_postal_address.split(" ")[-1],
              'CA',
              store_id,
              phone_no,
              '<MISSING>',
              lat,
              lon,
              store_opening_hours
            ])


    time.sleep(3)
    driver.quit()
    driver2.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
