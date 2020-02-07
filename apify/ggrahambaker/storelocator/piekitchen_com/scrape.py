import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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
    locator_domain = 'https://www.piekitchen.com/'
    ext = 'locations.html'

    driver = get_driver()
    driver.get(locator_domain + ext)

    main = driver.find_elements_by_css_selector('div.wsite-section-elements')[1]
    locs = main.find_elements_by_css_selector('tr.wsite-multicol-tr')
    loc_list = []
    for loc in locs:
        
        cont = loc.text.split('\n')
        print(cont)
        print()
        print()
        if 'We have Pie Kitchen locations to serve you in Louisville' in cont[0]:
            continue

        if len(cont) == 8 or len(cont) == 1:
            continue

        row = loc.find_elements_by_css_selector('tbody.wsite-multicol-tbody')

        print(len(row))

        if len(row) == 2:
            for r in row:
                tds = r.find_elements_by_css_selector('td.wsite-multicol-col')
                loc_list.append([tds[0], tds[1]])
        elif len(row) == 1:
            tds = loc.find_elements_by_css_selector('td.wsite-multicol-col')
            loc_list.append([tds[0], tds[1]])
            loc_list.append([tds[3], tds[4]])
        else:
            tds = loc.find_elements_by_css_selector('td.wsite-multicol-col')

            loc_list.append([tds[0], tds[1]])
            loc_list.append([tds[2], tds[3]])



    all_store_data = []
    for loc in loc_list:
        if 'franchising' in loc[1].text:
            continue

        href = loc[0].find_element_by_css_selector('iframe').get_attribute('src')
        start_idx = href.find('&long=') + 6
        end_idx = href.find('&domain')

        coords = href[start_idx:end_idx].split('&lat=')
        longit = coords[0]
        lat = coords[1]

        cont = loc[1].text.split('\n')

        if len(cont) == 7:
            location_type = 'Main Office'
            street_address = cont[1]
            city, state, zip_code = addy_ext(cont[2])
            phone_number = cont[3]
            hours = cont[-1]
        else:
            location_type = 'Store'
            street_address = cont[0]
            city, state, zip_code = addy_ext(cont[1])
            phone_number = cont[2]
            hours = ''
            for h in cont[4:]:
                hours += h + ' '

            hours = hours.strip()

        country_code = 'US'
        store_number = '<MISSING>'
        location_name = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)


    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
