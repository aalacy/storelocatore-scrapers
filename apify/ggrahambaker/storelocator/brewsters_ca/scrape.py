import csv
import os
from sgselenium import SgSelenium

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
    zip_code = state_zip[1] + ' ' + state_zip[2]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://brewsters.ca/'
    ext = 'find-us/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    lis = driver.find_elements_by_css_selector('a.icon-arrow-right')
    print(len(lis))
    link_list = []
    for li in lis:
        if len(li.get_attribute('href')) > 30:
            print(li.get_attribute('href'))
            link_list.append(li.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.implicitly_wait(10)
        driver.get(link)
        main = driver.find_element_by_css_selector('main#main')
        # main.find_element_by_css_selector
        print()
        print(main.text.split('\n'))
        content = main.text.split('\n')
        print(len(content))
        if len(content) == 17:
            location_name = content[1]
            street_address = content[4]

            print(content[4])
            print(content[5])
            city, state, zip_code = addy_ext(content[5])
            phone_number = content[6].replace('Phone:', '').replace('BREW', '2739').replace('HOPS', '4677')[:-7].strip()
            print(phone_number)
            print(content[9])
            hours = ''
            for h in content[9:-1]:
                hours += h + ' '
            hours = hours.strip()
            print(hours)
            print()
        else:
            location_name = content[1]
            street_address = content[5]

            print(content[5])
            print(content[6])
            city, state, zip_code = addy_ext(content[6])
            phone_number = content[7].replace('Phone:', '').replace('BREW', '2739').replace('HOPS', '4677')[:-7].strip()
            print(phone_number)
            hours = ''
            for h in content[10:-1]:
                hours += h + ' '
            hours = hours.strip()
            print(hours)

        location_name = '<MISSING>'
        country_code = 'CA'
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
