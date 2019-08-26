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


def clean(arr):
    to_ret = []
    for a in arr:
        if a == ' ':
            continue

        to_ret.append(a)

    return to_ret


def fetch_data():
    locator_domain = 'https://andpizza.com/'
    ext = 'shop-locations'

    driver = get_driver()
    driver.get(locator_domain + ext)

    tbodys = driver.find_elements_by_css_selector('tbody')
    all_store_data = []
    for tbody in tbodys:
        rows = tbody.find_elements_by_css_selector('tr')
        for row in rows:
            tds = row.find_elements_by_css_selector('td')
            for td in tds:
                cont = clean(td.text.split('\n'))
                print(cont)
                print(len(cont))
                if len(cont) == 0:
                    continue
                elif len(cont) == 14:
                    location_name = cont[0].strip()
                    street_address = cont[1]
                    city, state, zip_code = addy_ext(cont[3])

                    hours = ''
                    for h in cont[4:]:
                        hours += h + ' '

                    hours = hours.strip()

                else:
                    location_name = cont[0].strip()
                    if 'NORTH BETHESDA' in location_name:
                        street_address = cont[1]
                        city, state, zip_code = addy_ext(cont[3])
                        hours = ''
                        for h in cont[4:]:
                            hours += h + ' '

                        hours = hours.strip()
                    elif 'GAITHERSBURG' in location_name:
                        street_address = cont[1]
                        city, state, zip_code = addy_ext(cont[3])
                        hours = ''
                        for h in cont[4:]:
                            hours += h + ' '

                        hours = hours.strip()
                    elif 'THE MALL AT PRINCE GEORGES' in location_name:
                        street_address = cont[1] + ' ' + cont[2]
                        city, state, zip_code = addy_ext(cont[3])
                        hours = ''
                        for h in cont[4:]:
                            hours += h + ' '

                        hours = hours.strip()
                    elif 'WALNUT' in location_name:
                        street_address = cont[1]
                        city, state, zip_code = addy_ext(cont[3])
                        hours = ''
                        for h in cont[4:]:
                            hours += h + ' '

                        hours = hours.strip()

                    else:
                        street_address = cont[1]
                        city, state, zip_code = addy_ext(cont[2])

                        hours = ''
                        for h in cont[3:]:
                            hours += h + ' '

                        hours = hours.strip()

                lat = '<MISSING>'
                longit = '<MISSING>'
                country_code = 'US'
                store_number = '<MISSING>'
                phone_number = '<MISSING>'
                location_type = '<MISSING>'

                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                              store_number, phone_number, location_type, lat, longit, hours]
                all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
