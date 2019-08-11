import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', options=options)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code



def fetch_data():
    locator_domain = 'https://www.batterygiant.com/'
    ext = 'store-locator'

    driver = get_driver()
    driver.get(locator_domain + ext)

    tds = driver.find_elements_by_css_selector('td.storeLink')
    print(len(tds))
    link_list = []
    for td in tds:
        print(td.find_element_by_css_selector('a').get_attribute('href'))
        link_list.append(td.find_element_by_css_selector('a').get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        cont = driver.find_element_by_css_selector('div.grid_92')
        print()
        print(cont.text.split('\n'))
        content = cont.text.split('\n')
        print(len(content))
        if 'Panama' in content[0]:
            continue
        if len(content) == 13:
            print(content[3])
            street_address = content[3]
            city, state, zip_code = addy_ext(content[4])
            print(content[4])
            phone_number = content[6]
            print(content[6])
            hours = ''
            for h in content[10:]:
                hours += h + ' '
            hours = hours.strip()
            print(hours)
        elif len(content) == 16:
            if 'Louisville' in content[0]:
                print(content[5])
                street_address = content[5]
                print(content[6])
                city, state, zip_code = addy_ext(content[6])
                print(content[8])
                phone_number = content[8]
            else:
                print(content[6])
                street_address = content[6]
                print(content[7])
                city, state, zip_code = addy_ext(content[7])
                print(content[9])
                phone_number = content[9]
            print(content[13])
            hours = ''
            for h in content[13:]:
                hours += h + ' '
            hours = hours.strip()
            print(hours)
        elif len(content) < 11:
            if len(content) == 9:
                street_address = content[2] + ' ' + content[3]
                print(content[4])
                city, state, zip_code = addy_ext(content[4])
                print(content[6])
                hours = '<MISSING>'
                print(hours)
            else:
                street_address = content[2]
                print(content[3])
                city, state, zip_code = addy_ext(content[3])
                print(content[5])
                phone_number = content[5]
                print(content[7])
                hours = ''
                for h in content[7:]:
                    hours += h + ' '
                hours = hours.strip()
                print(hours)

        location_name = '<MISSING>'
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

        print()



    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
