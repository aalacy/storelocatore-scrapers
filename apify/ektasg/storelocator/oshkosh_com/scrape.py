import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('oshkosh_com')




options = Options()
#options.add_argument('--headless')
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
        writer.writerow(["locator_domain", "page_url" , "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    try:
        lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    except:
        lat = '<MISSING>'
    try:
        lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    except:
        lon = '<MISSING>'

    return lat, lon


def fetch_data():
            # Your scraper here
            data=[]
            count=0

            driver.get("https://www.oshkosh.com/on/demandware.store/Sites-Carters-Site/default/Stores-ShowAll")
            time.sleep(5)
            #driver.find_element_by_css_selector('a.close-popup').click()
            stores = driver.find_elements_by_css_selector('div.storeTile')
            page_url = "https://www.oshkosh.com/on/demandware.store/Sites-Carters-Site/default/Stores-ShowAll"
            for store in stores:
                location_name = store.find_element_by_css_selector('p.storeName').text.replace("\n", " ").replace("<br />", " ")
                try:
                    phone = store.find_element_by_css_selector('p.storePhone').text
                except:
                    phone = '<MISSING>'
                street_addr = store.find_element_by_css_selector('p:nth-child(2)').text
                if street_addr == '':
                    street_addr = '<MISSING>'
                    state_city_zip = store.find_element_by_css_selector('p:nth-child(3)').text
                else:
                    if store.find_element_by_css_selector('p:nth-child(4)').get_attribute('class') == 'storePhone':
                        state_city_zip = store.find_element_by_css_selector('p:nth-child(3)').text
                    elif store.find_element_by_css_selector('p:nth-child(4)').text == 'Map':
                        state_city_zip = store.find_element_by_css_selector('p:nth-child(3)').text
                    else:
                        street_addr = street_addr + store.find_element_by_css_selector('p:nth-child(3)').text
                        state_city_zip = store.find_element_by_css_selector('p:nth-child(4)').text
                city = state_city_zip.split(" ")[-3]
                state = state_city_zip.split(" ")[-2]
                zipcode = state_city_zip.split(" ")[-1]
                geomap = store.find_element_by_css_selector('a.googlemap').get_attribute('href')
                driver2.get(geomap)
                time.sleep(5)
                lat,lon = parse_geo(driver2.current_url)
                hours_of_op = '<MISSING>'
                data.append([
                     'https://www.oshkosh.com/',
                      page_url,
                      location_name,
                      street_addr,
                      city,
                      state,
                      zipcode,
                      'US',
                      '<MISSING>',
                      phone,
                      '<MISSING>',
                      lat,
                      lon,
                      hours_of_op
                    ])
                count+=1
                logger.info(count)
            driver.quit()
            driver2.quit()

            #driver3 = webdriver.Chrome("C:\chromedriver.exe", options=options)
            driver3 = webdriver.Chrome("chromedriver", options=options)
            #canada locations
            driver3.get("https://www.oshkosh.com/on/demandware.store/Sites-Carters-Site/default/Stores-International")
            time.sleep(5)
            page_url = "https://www.oshkosh.com/on/demandware.store/Sites-Carters-Site/default/Stores-International"
            #driver3.find_element_by_css_selector('a.close-popup').click()
            names = driver3.find_elements_by_css_selector('div.storeTile')
            for i in range(226,748):
                location_name = names[i].text.splitlines()[0].replace("@","").replace("&amp;"," ")
                location_type = names[i].get_attribute('class').split("storeTile ")[1]
                street_addr = names[i].find_element_by_css_selector('p:nth-child(3)').text
                state_city_zip = names[i].find_element_by_css_selector('p:nth-child(4)').text
                zipcode = state_city_zip.split(" ")[-2] + " " + state_city_zip.split(" ")[-1]
                zip_present = bool(re.search(r'\d', zipcode))
                if zip_present:
                    if len(state_city_zip.split(" ")[-1]) == 6:
                        zipcode = state_city_zip.split(" ")[-1]
                        state = state_city_zip.split(" ")[-2]
                        city_list = state_city_zip.split(" ")[0:-2]
                        city = " "
                        city.join(city_list)
                        if 'columbia' in state.lower() or 'brunswick' in state.lower() or 'scotia' in state.lower():
                            state = state_city_zip.split(" ")[-3] + " " + state_city_zip.split(" ")[-2]
                            city_list =  state_city_zip.split(" ")[0:-3]
                            city = " "
                            city.join(city_list)
                    else:
                        city_list = state_city_zip.split(" ")[0:-3]
                        city = " "
                        city.join(city_list)
                        state = state_city_zip.split(" ")[-3]
                        if 'columbia' in state.lower() or 'brunswick' in state.lower() or 'scotia' in state.lower():
                            state = state_city_zip.split(" ")[-4] + " " + state_city_zip.split(" ")[-3]
                            city_list =  state_city_zip.split(" ")[0:-4]
                            city = " "
                            city.join(city_list)
                else:
                    zipcode = '<MISSING>'
                    city_list = state_city_zip.split(" ")[0:-1]
                    city = " "
                    city.join(city_list)
                    state = state_city_zip.split(" ")[-1]


                try:
                    phone = names[i].find_element_by_css_selector('p:nth-child(5)').text.replace("BABY (","").replace(")","").replace(" (GIFT", "")
                except:
                    phone = '<MISSING>'
                data.append([
                    'https://www.oshkosh.com/',
                    page_url,
                    location_name,
                    street_addr,
                    city,
                    state,
                    zipcode,
                    'CA',
                    '<MISSING>',
                    phone,
                    location_type,
                    '<MISSING>',
                    '<MISSING>',
                    '<MISSING>'
                ])
                count += 1
                logger.info(count)

            time.sleep(3)
            driver3.quit()
            return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()