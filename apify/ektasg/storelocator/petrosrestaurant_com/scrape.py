import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
import re
import usaddress
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('petrosrestaurant_com')



options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--disable-plugins")
options.add_argument( "--no-experiments")
options.add_argument( "--disk-cache-dir=null")

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
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon



def fetch_data():
    data=[]
    driver.get("https://www.petrosbrand.com/locations")
    stores=driver.find_elements_by_xpath("//div[contains(@class,'col-sm-6')]//a")
    li = [stores[i].get_attribute('href') for i in range(0,len(stores))]
    for i in range(len(li)):
        driver.get(li[i])
        time.sleep(5)
        page_url = li[i]
        store_opening_hours=driver.find_element_by_xpath("//div[@class='text-box']/div[@class='field field--name-field-text field--type-text-long field--label-hidden field--item']").get_attribute("textContent")
        hour = store_opening_hours.replace('\n', ' ')
        location_name=driver.find_element_by_xpath('//h1[@class="page-header"]').get_attribute("textContent")
        logger.info("location_name:     " , location_name)
        address=driver.find_element_by_xpath("//div[@class='container']//p").get_attribute("textContent")
        tagged = usaddress.tag(address)[0]
        try:
            street_addr = tagged['Recipient'] + " "+ tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + \
                          tagged['StreetNamePostType'].split('\n')[0] + " " + \
                          tagged['OccupancyType'] + " " + tagged['OccupancyIdentifier'].split('\n')[0]
        except:
            try:
                street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0] + " " + tagged['OccupancyIdentifier'].split('\n')[0]
            except:
                try:
                    street_addr = tagged['AddressNumber'] + " " + tagged['StreetNamePreDirectional'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
                except:
                    try:
                        street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostDirectional'].split('\n')[0] + " " +tagged['StreetNamePostType'].split('\n')[0]
                    except:
                        try:
                            street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostDirectional'].split('\n')[0]
                        except:
                            try:
                                street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
                            except:
                                street_addr = tagged['AddressNumber'] + " " + tagged['StreetName']
        state = tagged['StateName']
        zipcode = tagged['ZipCode']
        city = tagged['PlaceName']
        geomap = driver.find_element_by_xpath("//a[contains(@href,'//goo.gl/maps')]").get_attribute('href')
        driver2.get(geomap)
        time.sleep(5)
        lat, lon = parse_geo(driver2.current_url)
        try:
            loc_text = driver.find_elements_by_css_selector('div.field.field--name-field-text.field--type-text-long.field--label-hidden.field--item')
        except:
            loc_text = driver.find_elements_by_css_selector('div.field.field--name-field-text2.field--type-text-long.field--label-hidden.field--item')

        for loc in loc_text:
            try:
                element = loc.find_element_by_css_selector('h2').text
                if element.lower() == 'location':
                    phone_no = loc.find_element_by_css_selector('p:nth-child(3)').text.splitlines()[0]
                    break
            except:
                pass

        country = 'US'
        data.append([
            'www.petrosbrand.com',
            page_url,
            location_name,
            street_addr,
            city,
            state,
            zipcode,
            country,
            '<MISSING>',
            phone_no,
            '<MISSING>',
            lat,
            lon,
            hour                     
           ])

    time.sleep(3)
    driver2.quit()
    driver.quit()
    return data

         
def scrape():
        data = fetch_data()
        write_output(data)

scrape()