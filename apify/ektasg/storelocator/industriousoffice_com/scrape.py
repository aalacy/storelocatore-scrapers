import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
import re 

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--disable-plugins")
options.add_argument( "--no-experiments")
options.add_argument( "--disk-cache-dir=null")

#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon



def fetch_data():
    data=[]
    driver.delete_all_cookies()
    driver.get("https://www.industriousoffice.com/locations?nabt=1")
    time.sleep(10)
    latlnglocations = driver.execute_script("return locationsCords;")
    list_url=[]
    k=driver.find_elements_by_xpath("//a[contains(@class,'btn-location')]")
    for j in k:
        list_url.append(j.get_attribute('href')) 
    for x in list_url:
        driver.get(x)
        try:
            globalvar = driver.execute_script("return marketLocations;")
            for i in range(0,len(globalvar)):
                location_name = globalvar[i]['title'].replace(",","")
                latitude = globalvar[i]['latitude']
                longitude = globalvar[i]['longitude']
                street_addr = globalvar[i]['address']
                city = globalvar[i]['city']
                state= globalvar[i]['state']
                zipcode = globalvar[i]['zip']
                phone = globalvar[i]['phone']
                data.append([
                    'https://www.industriousoffice.com/',
                    location_name,
                    street_addr,
                    city,
                    state,
                    zipcode,
                    'US',
                    '<MISSING>',
                    phone,
                    '<MISSING>',
                    latitude,
                    longitude,
                    '<MISSING>'
                ])

        except:
            try:
                location_name = driver.find_element_by_xpath("//span[contains(@class,'addressLocality')]").text.replace(",","")
                phone = driver.find_element_by_xpath("//span[contains(@class,'phone')]").text
                street_addr = driver.find_element_by_xpath("//span[contains(@class,'streetAddress')]").text
                city = driver.find_element_by_xpath("//span[contains(@class,'addressLocality')]").text
                state = driver.find_element_by_xpath("//span[contains(@class,'addressRegion')]").text
                zipcode = driver.find_element_by_xpath("//span[contains(@class,'postalCode')]").text
                latitude ='<MISSING>'
                longitude = '<MISSING>'
                data.append([
                    'https://www.industriousoffice.com/',
                    location_name,
                    street_addr,
                    city,
                    state,
                    zipcode,
                    'US',
                    '<MISSING>',
                    phone,
                    '<MISSING>',
                    latitude,
                    longitude,
                    '<MISSING>'
                ])
            except:
                pass

    for i in range(0,len(latlnglocations)):
        lat = latlnglocations[i]['lat']
        long = latlnglocations[i]['lng']
        title =latlnglocations[i]['title']
        for j in range (0,len(data)):
            if data[j][1] in title:
                data[j][10] = lat
                data[j][11] = long
                break

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()



