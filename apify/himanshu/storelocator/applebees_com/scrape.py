import csv
from bs4 import BeautifulSoup
import time
import re
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver import Firefox
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import platform
system = platform.system()


def get_driver():
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')

    # profile = webdriver.FirefoxProfile('C:\\Users\\01\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\3fz3yyhy.default-release')
    profile = webdriver.FirefoxProfile()

    PROXY_HOST = "12.12.12.123"
    PROXY_PORT = "1234"
    profile.set_preference("network.proxy.type", 1)
    profile.set_preference("network.proxy.http", PROXY_HOST)
    profile.set_preference("network.proxy.http_port", int(PROXY_PORT))
    profile.set_preference("dom.webdriver.enabled", False)
    profile.set_preference('useAutomationExtension', False)
    profile.update_preferences()
    desired = DesiredCapabilities.FIREFOX

    return Firefox(firefox_profile=profile, desired_capabilities=desired,options=options)



def write_output(data):
    with open('data.csv', mode='w',newline ="", encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    addresses = []
    base_url = "https://www.applebees.com/"
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = "presidentebarandgrill"
    latitude = ""
    longitude = ""
    raw_address = ""
    hours_of_operation = ""
    driver = get_driver()

    list_urls = []
    driver.get("https://www.applebees.com/en/sitemap")
    soup = BeautifulSoup(driver.page_source,"lxml")
    for link in soup.find("div",class_="site-map").find_all("ul")[7:]:
        for a in link.find_all("a",class_="nav-link"):
            a = "https://www.applebees.com"+a["href"]
            # print(a)
            list_urls.append(a)
    dict_urls = { i : list_urls[i] for i in range(0, len(list_urls) ) }
    # print(dict_urls)
    
    index1=0
    for q in range(0,len(dict_urls),5):
        if q==0:
            index1=0
            pass
        else:
            for data1 in range(index1,q):
                if data1 in dict_urls:
                    #print("index1 == ",index1,"q == ",q)
                    #print(dict_urls[data1])
                    try:
                        driver.get(dict_urls[data1])
                        time.sleep(2)
                    except:
                        #print("-------",dict_urls[data1])
                        continue
                     
                    soup1 = BeautifulSoup(driver.page_source,"lxml")
                    loc_section = soup1.find("div",{"id":"location-cards-wrapper"})
                    for loc_block in loc_section.find_all("div",class_="owl-item"):
                        country_code = loc_block.find("input",{"name":"location-country"})["value"]
                        geo_code = loc_block.find("input",{"name":"location-country"}).nextSibling.nextSibling
                        latitude = geo_code["value"].split(",")[0]
                        longitude = geo_code["value"].split(",")[1].split("?")[0]
                        page_url ="https://www.applebees.com"+ loc_block.find("div",class_="map-list-item-header").find("a")["href"]
                        location_name = loc_block.find("div",class_="map-list-item-header").find("span",class_="location-name").text.strip()
                        address = loc_block.find("div",class_="address").find("a",{"title":"Get Directions"})
                        address_list = list(address.stripped_strings)
                        street_address = " ".join(address_list[:-1]).strip()
                        city = address_list[-1].split(",")[0].strip()
                        state = address_list[-1].split(",")[1].split()[0].strip()
                        zipp = address_list[-1].split(",")[1].split()[-1].strip()
                        phone = loc_block.find("a",class_="data-ga phone js-phone-mask").text.strip()
                        store_number= "<MISSING>"
                        driver.get(page_url)
                        time.sleep(2)
                        soup2 = BeautifulSoup(driver.page_source,"lxml")
                        try:
                            hours_of_operation = " ".join(list(soup2.find("div",class_="hours").stripped_strings))
                        except :
                            hours_of_operation = "<MISSING>"
                        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                        store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]

                        if str(store[-1]) not in addresses:
                            addresses.append(str(store[-1]))

                            store = [x if x else "<MISSING>" for x in store]

                            #print("data = " + str(store))
                            #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                            yield store
            index1 +=5
            driver.close()
            time.sleep(2)
            driver = get_driver()

    driver.quit()

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
