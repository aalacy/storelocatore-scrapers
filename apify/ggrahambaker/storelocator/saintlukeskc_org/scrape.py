import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

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



def parse_addy(addy):
    arr = addy.split(',')
    if len(arr) == 4:
        arr = [arr[0], arr[2], arr[3]]
    street_address = arr[0].strip()
    city = arr[1].strip()
    state_zip = arr[2].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    
    
    return street_address, city, state, zip_code


def fetch_data():
    locator_domain = 'https://www.saintlukeskc.org/'

    driver = get_driver()
    driver.get(locator_domain)
    driver.implicitly_wait(5)

    link = driver.find_element_by_xpath('//a[contains(text(),"Locations")]')
    html = link.find_element_by_xpath('..').find_element_by_css_selector('ul').get_attribute('innerHTML')

    soup = BeautifulSoup(html, 'html.parser')

    cats = soup.find_all('a')

    cat_links = [[cat.text, locator_domain[:-1] + cat['href']] for cat in cats]


    all_store_data = []
    for cat_obj in cat_links:
        location_type = cat_obj[0]
        link = cat_obj[1]
        #if 'location?field_location_type_target_id' not in link:
        #    print(link)
        #    #continue
        driver.get(link)
        driver.implicitly_wait(5)
        
        next_button = driver.find_elements_by_css_selector('li.pager__item--next')
        while len(next_button) > 0:
            time.sleep(2)
            print('done sleep')
            
            locs = driver.find_elements_by_css_selector('div.geolocation')
            print(len(locs))
            for loc in locs:
                lat = loc.get_attribute('data-lat')
                longit = loc.get_attribute('data-lng')
                
                location_name = loc.find_element_by_css_selector('h4').text
                print(location_name)
                addy = loc.find_element_by_css_selector('p.address').text
            
                street_address, city, state, zip_code = parse_addy(addy)

                street_address = street_address.split('Ste ')[0]

                has_phone_number = loc.find_elements_by_css_selector('a.tel__number')

                if len(has_phone_number) > 0:
                    phone_number = has_phone_number[0].text
                else:
                    phone_number = '<MISSING>'
                
                
                country_code = 'US'
                
                
                button = loc.find_elements_by_css_selector('div.location-result__button-wrapper')
                if len(button) > 0:
                    page_url = button[0].find_element_by_css_selector('a').get_attribute('href')
                else:
                    page_url = '<MISSING>'


                hours = '<MISSING>'
                store_number = '<MISSING>'
                street_address = street_address.split('Suite')[0].strip().split('Unit')[0].strip().replace(',', '').strip()

                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                            store_number, phone_number, location_type, lat, longit, hours, page_url]

    
                all_store_data.append(store_data)
                
                
            
            next_button[0].find_element_by_css_selector('a').click()
            
            time.sleep(2)
            next_button = driver.find_elements_by_css_selector('li.pager__item--next')
            driver.implicitly_wait(5)
            
            


    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
