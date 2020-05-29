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

def fetch_data():
    locator_domain = 'https://www.terroni.com/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain)

    tor_locs = driver.find_element_by_css_selector('nav#nav-footer-left').find_elements_by_css_selector('a')
    ny_locs = driver.find_element_by_css_selector('nav#nav-footer-middle').find_elements_by_css_selector('a')

    all_locs = tor_locs + ny_locs

    link_list = []
    for loc in all_locs:
        link = loc.get_attribute('href')
        if '#' in link:
            break
        link_list.append(link)

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(15)
        addy = driver.find_elements_by_css_selector('address.location-reservation-address')
        if len(addy) == 1:
            idx = link[:-1].rfind('/')
            location_name = link[idx:][:-1].replace('-', ' ').replace('/', '')

            phone_number = driver.find_element_by_xpath("//a[contains(@href, 'tel:')]").get_attribute('href').replace(
                'tel:', '')
            addy_href = addy[0].find_element_by_css_selector('a').get_attribute('href')
            street_addy_idx = addy_href.find('place/') + 6
            coord_start_idx = addy_href.find('/@')

            address = addy_href[street_addy_idx:coord_start_idx].split(',')
            street_address = address[0].replace('+', ' ').strip()
            city = address[1].replace('+', ' ').strip()
            if 'USA' in addy_href:
                addy_split = address[2].replace('+', ' ').strip().split(' ')
                state = addy_split[0]
                zip_code = addy_split[1].strip()
                country_code = 'US'
            else:
                addy_split = address[2].replace('+', ' ').strip().split(' ')
                country_code = 'CA'
                if len(addy_split) == 2:
                    state = addy_split[0]
                    zip_code = '<MISSING>'
                else:
                    state = addy_split[0]
                    zip_code = addy_split[1] + ' ' + addy_split[2]

            coords = addy_href[coord_start_idx + 2:].split(',')
            lat = coords[0]
            longit = coords[1]

            content = driver.find_element_by_xpath('//div[@data-section="content"]')
            p_hours = content.find_element_by_xpath('//div[@data-align="right"]').find_elements_by_css_selector('p')
            hours = ''
            for p in p_hours:
                hours += p.text + ' '

            hours = hours.replace('HOURS', '').replace(':', '').replace('SEE MENU & ORDER ONLINE', '').strip()
        else:
            footer = driver.find_elements_by_css_selector('footer.site-footer')
            if len(footer) == 1:
                location_name = 'DOPOLAVORO'
                cont = footer[0].find_element_by_css_selector('div.grid')
                cont_p = cont.find_elements_by_css_selector('p')
                address = cont_p[0].text.split(',')

                street_address = address[0]
                city = address[1].strip()
                state_zip = address[2].strip().split(' ')
                state = state_zip[0]
                zip_code = state_zip[1]
                country_code = 'US'

                hours_phone = cont_p[1].text.split('-')
                hours = hours_phone[0] + '-' + hours_phone[1]
                phone_number = hours_phone[2] + '-' + hours_phone[3]

            else:
                continue

        store_number = '<MISSING>'
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
