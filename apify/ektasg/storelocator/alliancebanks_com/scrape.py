import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('alliancebanks_com')




options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    count=0
    data=[]
    driver.get("https://www.alliancebanks.com/locations/index.html")
    time.sleep(3)
    stores = driver.find_elements_by_link_text('More Information')
    name = [stores[i].get_attribute('href') for i in range(0, len(stores))]
    
    for i in range(0,len(name)):
        driver.get(name[i])
        time.sleep(2)
        location_name= driver.find_element_by_css_selector('div.container.col-md-6.addresshours >h2').text
        info = driver.find_element_by_css_selector('div.container.col-md-6.addresshours').text
        hours_of_op = 'Lobby' +  info.split('Lobby')[1]
        phone = "(" + info.split('Lobby')[0].split('(')[1]

        address = info.split('Lobby')[0].split('(')[0]
        address_split = address.splitlines()
        state_ciy_zip = address_split[len(address_split)-1]
        zipcode = state_ciy_zip.split(" ")[-1]
        state = state_ciy_zip.split(" ")[-2]
        city = state_ciy_zip.split(",")[0]
        if len(address_split) == 4:
            street_addr = address_split[1] + " " + address_split[2]
        else:
            street_addr = address_split[1]
        data.append([
                'https://www.alliancebanks.com/',
                name[i],
                location_name,
                street_addr,
                city,
                state,
                zipcode,
                'US',
                '<MISSING>',
                phone.replace('\n',''),
                '<MISSING>',
                '<MISSING>',
                '<MISSING>',
                hours_of_op.replace('\n','').replace('Drive',' Drive').replace('Walk',' Walk').replace('Friday','Friday ').replace('  ',' ')
            ])
        #logger.info(count,data[count])
        count = count + 1
       
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
