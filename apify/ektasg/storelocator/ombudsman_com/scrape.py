import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('ombudsman_com')



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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)




def fetch_data():

    data = []
    driver.get("https://www.ombudsman.com/locations/")
    time.sleep(5)
    count=0

    stores = driver.find_elements_by_css_selector('ul.state-list-column >li >a')
    names = [stores[i].get_attribute("href") for i in range(0, len(stores))]
    for i in range(0, len(names)):
            driver2.get(names[i])
            time.sleep(5)
            page_url = names[i]
            logger.info(page_url)
            lat=[]
            lng=[]
            coords = driver2.find_elements_by_xpath("//script[@type='text/javascript']")
            for j in range(len(coords)):
                text = coords[j].get_attribute('innerHTML')
                if "mapp.data.push" in text:
                    split_text = text.split('"pois":')[1].split('} );')[0]
                    json_Data = json.loads(split_text)
                    break
                else:
                    pass
            try:
                state_stores = driver2.find_elements_by_css_selector('ul.state-list-column > li')
                #logger.info("isnide try state_stores........." , state_stores)
            except:
                pass
            k=0
            for state_store in state_stores:
                store_name= state_store.find_element_by_css_selector('h4').text
                logger.info(store_name)
                lat = json_Data[k]['point']['lat']
                lng= json_Data[k]['point']['lng']
                try:
                    street_addr = state_store.find_element_by_css_selector("span[itemprop=streetAddress").text
                    state= state_store.find_element_by_css_selector("span[itemprop=addressRegion").text
                    city= state_store.find_element_by_css_selector("span[itemprop=addressLocality").text
                    zipcode = state_store.find_element_by_css_selector("span[itemprop=postalCode").text.splitlines()[0]
                except:
                    address = state_store.find_element_by_css_selector('p').text.splitlines()
                    if len(address) ==2:
                        street_addr = address[0]
                        zipcode = address[1].split(" ")[-1]
                        state = address[1].split(" ")[-2]
                        city_list = address[1].split(" ")[:-2]
                        if len(city_list) == 1:
                            city = city_list[0]
                        else:
                            city = city_list[0]+" " + city_list[1]
                    elif len(address) == 3:
                        street_addr = address[0]+ " " + address[1]
                        zipcode = address[2].split(" ")[-1]
                        state = address[2].split(" ")[-2]
                        city_list = address[2].split(" ")[:-2]
                        if len(city_list) == 1:
                            city = city_list[0]
                        else:
                            city = city_list[0]+" " + city_list[1]
                try:
                    phone_no = state_store.find_element_by_css_selector("span[itemprop=telephone]").text
                except:
                    phone_no = '<MISSING>'
                data.append([
                     'https://www.ombudsman.com/',
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
                      lng,
                      '<MISSING>'
                    ])
                count+=1
                k+=1
                logger.info(count)


    time.sleep(3)
    driver.quit()
    driver2.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
