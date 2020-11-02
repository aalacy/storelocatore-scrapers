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
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.firstchoicedental.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(30)
    nav = driver.find_element_by_css_selector('nav.footerNav')
    nav2 = nav.find_element_by_css_selector('div.col-md-3')
    hrefs = nav2.find_elements_by_css_selector('a')

    link_list = []
    for href in hrefs:
        if len(href.get_attribute('href')) > 45:
            link_list.append([href.get_attribute('href')])

    locs = driver.find_elements_by_css_selector('div.list-content')
    for i, loc in enumerate(locs):
        phone = loc.find_element_by_css_selector('p.tel-holder').find_element_by_css_selector('a').get_attribute(
            'href').replace('tel:', '')
        link_list[i].append(phone)

    all_store_data = []
    for link in link_list:
        driver.get(link[0])
        driver.implicitly_wait(30)
        div_cont = driver.find_element_by_css_selector('div.location-detail__contact')

        details = div_cont.text.split('\n')
        if len(details) == 21:
            if '608.848.0820' in details[1]:
                street_address = details[5]
                city, state, zip_code = addy_ext(details[6])
                hours = ''
                for h in details[11:-3]:
                    hours += h + ' '
                hours = hours.strip()

            else:
                street_address = details[3]
                city, state, zip_code = addy_ext(details[4])
                hours = ''
                for h in details[9:-3]:
                    hours += h + ' '
                hours = hours.strip()

        elif len(details) == 19:
            street_address = details[3]
            city, state, zip_code = addy_ext(details[4])
            hours = ''
            for h in details[7:-3]:
                hours += h + ' '
            hours = hours.strip()

        elif len(details) == 23:
            street_address = details[5]
            city, state, zip_code = addy_ext(details[6])
            hours = ''
            for h in details[11:-3]:
                hours += h + ' '
            hours = hours.strip()

        elif len(details) == 24:
            street_address = details[5] + ' ' + details[6]
            city, state, zip_code = addy_ext(details[7])

            hours = ''
            for h in details[12:-3]:
                hours += h + ' '
            hours = hours.strip()

        phone_number = link[1]
        location_name = '<MISSING>'
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = details[-1].replace(' | ', ', ')

        lat = '<MISSING>'
        longit = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
