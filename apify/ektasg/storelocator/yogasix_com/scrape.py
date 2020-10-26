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


def parse_geo(url):
    try:
        lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    except:
        lon = re.findall(r'\,(-?[\d\.]*)', url)[0]
    try:
        lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    except:
        try:
            lat = re.findall(r'/@(-?[\d\.]*)', url)[0]
        except:
            lat = '<MISSING>'
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
    driver.get("https://www.yogasix.com/location-search")
    time.sleep(5)
    count=0
    while True:
        try:
            driver.find_element_by_xpath("//button[@class='location-search-list__showMore']").click()
            time.sleep(5)
        except:
            break


    stores = driver.find_elements_by_xpath("//a[contains(@class,'button button--primary location-search-list__cta')]")
    names = [stores[i].get_attribute("href") for i in range(0, len(stores))]
    for i in range(len(names)):
        driver2.get(names[i])
        time.sleep(5)
        page_url = names[i]
        print(names[i])
        #print(driver2.find_element_by_class_name("location-info-map__details-inner-container").get_attribute("innerText"))
        if "coming soon" in driver2.find_element_by_class_name("location-info-map__details-inner-container").get_attribute("innerText").lower():

            print("coming soon")
            continue
        else:
            store_name=driver2.find_element_by_tag_name('title').get_attribute('textContent').strip()
            #print(store_name)
            try:
                hours_elems =driver2.find_elements_by_css_selector('div.map__days')
                if hours_elems == []:
                    store_opening_hours = '<MISSING>'
                else:
                    store_opening_hours =""
                    for j in range(len(hours_elems)):
                        store_opening_hours = store_opening_hours + " " + hours_elems[j].get_attribute('textContent').replace("\n"," ")
            except:
                store_opening_hours = '<MISSING>'
            try:
                phone_no =driver2.find_element_by_xpath("//a[contains(@href,'tel:')]").get_attribute('textContent').replace("\n","").replace(" ","")
            except:
                phone_no = '<MISSING>'
            elem = driver2.find_element_by_class_name("location-info-map__info").find_element_by_tag_name('a')
            #geomap = elem.get_attribute('href')
            #store_address = elem.get_attribute("innerHTML")
            store_address = elem.get_attribute("text").strip()
            #print(store_address)
            street_addr= store_address.split("\n")[0].strip()
            state= store_address.split("\n")[1].split(",")[1].split(" ")[-2]
            city= store_address.split("\n")[1].split(",")[0].strip()
            zipcode = store_address.split("\n")[1].split(",")[1].split(" ")[-1]
            coords=driver2.find_element_by_id("map").get_attribute("data-location").replace("[","").replace("]","").split(",")
            lon=coords[0].strip()
            lat=coords[1].strip()
            #print(lat,lon)
            #geomap = driver2.find_element_by_xpath("//a[contains(@itemprop, 'address')]").get_attribute('href')
            #driver3.get(geomap)
            #time.sleep(5)
            #lat, lon = parse_geo(driver3.current_url)
            data.append([
                 'https://www.yogasix.com/',
                  page_url,
                  store_name,
                  street_addr,
                  city,
                  state,
                  zipcode,
                  'US',
                  '<MISSING>',
                  phone_no,
                  '<MISSING>',
                  lat,
                  lon,
                  store_opening_hours
                ])
            count+=1
            #print(count)


    time.sleep(3)
    driver.quit()
    driver2.quit()
    driver3.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
