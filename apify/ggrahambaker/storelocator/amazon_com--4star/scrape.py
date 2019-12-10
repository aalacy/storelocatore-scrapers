import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import usaddress

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
    parsed_add = usaddress.tag(addy)[0]

    street_address = ''

    if 'AddressNumber' in parsed_add:
        street_address += parsed_add['AddressNumber'] + ' '
    if 'StreetNamePreDirectional' in parsed_add:
        street_address += parsed_add['StreetNamePreDirectional'] + ' '
    if 'StreetNamePreType' in parsed_add:
            street_address += parsed_add['StreetNamePreType'] + ' '
    if 'StreetName' in parsed_add:
        street_address += parsed_add['StreetName'] + ' '
    if 'StreetNamePostType' in parsed_add:
        street_address += parsed_add['StreetNamePostType'] + ' '
    if 'OccupancyType' in parsed_add:
        street_address += parsed_add['OccupancyType'] + ' '
    if 'OccupancyIdentifier' in parsed_add:
        street_address += parsed_add['OccupancyIdentifier'] + ' ' 

    street_address = street_address.strip()
    city = parsed_add['PlaceName'].strip()
    state = parsed_add['StateName'].strip()
    zip_code = parsed_add['ZipCode'].strip()
    
    return street_address, city, state, zip_code


def fetch_data():
    locator_domain = 'https://amazon.com/4star'
    loc_url = 'https://www.amazon.com/b/ref=s9_acss_bw_cg_A4S_1a1_w?node=17608448011&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-1&pf_rd_r=65J1BBEFCG70MGVSTQB0&pf_rd_t=101&pf_rd_p=eb3c6053-8d6b-4f16-8e09-b9270e8e27b3&pf_rd_i=17988552011#Amazon4starLocations'
    driver = get_driver()
    driver.get(loc_url)
    driver.implicitly_wait(20)
    hrefs = driver.find_elements_by_xpath("//a[contains(@href, '&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-6&pf_rd_r')]")


    link_list = []
    for href in hrefs[1:]:
        link = href.get_attribute('href')
        link_list.append(link)


    all_store_data = []
    print(len(link_list))
    for link in link_list:
    
        driver.get(link)
        driver.implicitly_wait(10)
        
        loc_anchor = driver.find_element_by_xpath("//h2[contains(text(),'Amazon 4-star')]").find_element_by_xpath('..')
        location_name = loc_anchor.find_element_by_css_selector('a').text

        cont = loc_anchor.find_elements_by_xpath('p')
        phone_number = cont[1].text.replace('Phone:', '')
        if 'To come' in phone_number:
            continue
        
        google_link = cont[0].find_element_by_css_selector('a').get_attribute('href')
        start = google_link.find('/@')
        if start > 0:
            end = google_link.find('z/data')
            coords = google_link[start+2:end].split(',')
            lat = coords[0]
            longit = coords[1]
        else:
            lat = '<MISSING>'
            longit = '<MISSING>'
        addy = cont[0].text.replace('Address:', '').strip()

        street_address, city, state, zip_code = parse_addy(addy)
                    
        hours = ''
        
        for h in cont[2:]:
            if 'Regular Hours' in h.text:
                continue
            if 'Holiday' in h.text:
                break
            
            hours += h.text + ' '
        
        country_code = 'US'

        page_url = link

        store_number = '<MISSING>'
        location_type = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)


    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
