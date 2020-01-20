import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.childrensplace.com/'
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    driver = get_driver()
    driver.get('https://www.childrensplace.com/us/stores')
    driver.implicitly_wait(10)
    
    store_names = driver.find_elements_by_css_selector('h2.store-name')
    link_list = []
    
    for store in store_names:
        link = store.find_element_by_css_selector('a').get_attribute('href')
        link_list.append(link)
        


    driver.quit()


    all_store_data = []
    
    for link in link_list:
        r = session.get(link, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        location_name = soup.find('h2', {'itemprop': 'name'}).text
        
        addy = str(soup.find('address')).split('<address class="store-address">')[1].split('<br/>')
        street_address = addy[0]
        
        addy_ext = addy[1].replace('</address>', '').strip().split(',')
        city = addy_ext[0].strip()
        state = addy_ext[1].strip()
        zip_code = addy_ext[2].strip()
        if len(zip_code) == 6:
            zip_code = zip_code.upper()[:3] + ' ' + zip_code.upper()[3:]
            country_code = 'CA'
        else:
            country_code = 'US'

    
        
        phone_number = soup.find('p', {'class': 'store-phone-number'}).text

        store_number = '<MISSING>'
        
        location_type = soup.find('div', {'class': 'store-information'}).text

        
        if 'CLOSED' in soup.find('div', {'class': 'regular-time-schedules'}).text:
            continue
        hours = ''
        
        days = soup.find_all('li', {'class': 'day-and-time-item-container'})
        for d in days:
            day_name = d.find('span', {'class': 'day-name-container'}).text
            if day_name in hours:
                break
            day_hours = d.find('span', {'class': 'hoursRange'}).text
                
            hours += day_name + ' ' + day_hours + ' '
            
        hours = hours.strip()
        
        lat = '<MISSING>'
        longit = '<MISSING>'

        location_type = '<MISSING>'
        page_url = link
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)
        


    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
