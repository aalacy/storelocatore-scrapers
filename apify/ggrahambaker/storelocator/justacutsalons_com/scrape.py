import csv
import os
from sgselenium import SgSelenium

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
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
    locator_domain = 'http://www.justacutsalons.com/'
    ext = 'locations-1'

    driver = SgSelenium().chrome()
    base_link = locator_domain + ext
    driver.get(base_link)
    main = driver.find_element_by_css_selector('div#page-569f942c1a5203d45fe31ec5')
    ps = main.find_elements_by_css_selector('p')
    spin = 0
    bad_fixed = False
    all_store_data = []
    for p in ps:
        cont = p.text.split('\n')
        if len(cont) > 1:
            if spin == 0:
                cont = p.text.split('\n')
                street_address = cont[0]
                if "pm" in street_address:
                    continue
                city, state, zip_code = addy_ext(cont[1])
                state = state.replace('.', '')
                phone_number = cont[2].replace('PHONE:', '').strip()
                spin = 1
            else:
                hours = p.text.replace('\n', ' ')

                lat = '<MISSING>'
                longit = '<MISSING>'
                country_code = 'US'
                store_number = '<MISSING>'
                location_type = '<MISSING>'
                location_name = '<MISSING>'
                if "Cesar Chavez" in hours and bad_fixed == False:
                    print("fixing")
                    hours = "Temporarily Closed"
                    store_data = [locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code,
                                  store_number, phone_number, location_type, lat, longit, hours]
                    all_store_data.append(store_data)
                    bad_fixed = True
                    street_address = "105 N. Cesar Chavez St. STE. 9"
                    city = "San Juan"
                    state = "TX"
                    zip_code = "78589"
                    phone_number = "(956) 223-4070"
                    hours = "MON - FRI: 10:00am - 7:00pm SATURDAY: 9:00am - 6:00pm SUNDAY: 9:00am - 6:00pm"
                    store_data = [locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code,
                                  store_number, phone_number, location_type, lat, longit, hours]
                    all_store_data.append(store_data)
                    spin = 0
                    continue
                else:
                    store_data = [locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code,
                                  store_number, phone_number, location_type, lat, longit, hours]                    

                all_store_data.append(store_data)
                spin = 0

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
