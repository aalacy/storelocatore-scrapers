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
    locator_domain = 'https://www.firstchoicedental.com/'
    ext = 'locations/'

    driver = get_driver()
    driver.get(locator_domain + ext)

    nav = driver.find_element_by_css_selector('nav.footerNav')
    nav2 = nav.find_element_by_css_selector('div.col-md-3')
    hrefs = nav2.find_elements_by_css_selector('a')

    link_list = []
    for href in hrefs:
        if len(href.get_attribute('href')) > 45:
            link_list.append(href.get_attribute('href'))



    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(30)
        div_cont = driver.find_element_by_css_selector('div.location-detail__contact')
        details = div_cont.text.split('\n')

        if len(details) == 23:
            phone_number = details[1]
            if '608.205.3280' in phone_number:
                street_address = details[7]
                city, state, zip_code = addy_ext(details[8])
                hours = ''
                for h in details[13:-3]:
                    hours += h + ' '
                hours = hours.strip()

            else:
                street_address = details[5]
                city, state, zip_code = addy_ext(details[6])
                hours = ''
                for h in details[11:-3]:
                    hours += h + ' '
                hours = hours.strip()

        elif len(details) == 21:
            phone_number = details[1]

            street_address = details[5]

            city, state, zip_code = addy_ext(details[6])
            hours = ''
            for h in details[9:-3]:
                hours += h + ' '
            hours = hours.strip()

        elif len(details) == 25:
            phone_number = details[1]

            street_address = details[7]
            city, state, zip_code = addy_ext(details[8])
            hours = ''
            for h in details[13:-3]:
                hours += h + ' '
            hours = hours.strip()

        elif len(details) == 26:
            phone_number = details[1]
            street_address = details[7] + ' ' + details[8]
            city, state, zip_code = addy_ext(details[9])

            hours = ''
            for h in details[14:-3]:
                hours += h + ' '
            hours = hours.strip()


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
