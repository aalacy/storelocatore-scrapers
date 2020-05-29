import csv
import os
from sgselenium import SgSelenium
from selenium.common.exceptions import NoSuchElementException
import usaddress

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def parse_addy(addy):
    if '10250 Santa Monica Blvd Suite 9255' in addy:
        street_address = '10250 Santa Monica Blvd Suite 9255 (2nd floor)'
        city = 'Los Angeles'
        state = 'CA'
        zip_code = '90067'
    else:    
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
    locator_domain = 'https://amazon.com/presentedbyamazon'
    loc_url = 'https://www.amazon.com/b/ref=s9_acss_bw_cg_ABFYSA_3d1_w?node=17608448011&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-1&pf_rd_r=7W7N7KDK6FD75SGKEXEC&pf_rd_t=101&pf_rd_p=051f1019-a5e5-4cba-8c2a-13a383a7cfd2&pf_rd_i=17608448011#AmazonPopUpLocations'

    driver = SgSelenium().chrome()
    driver.get(loc_url)

    hrefs = driver.find_elements_by_xpath("//a[contains(@href, 'pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-10&')]")

    link_list = []
    for href in hrefs:
        link = href.get_attribute('href')

        link_list.append(link)

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        
        try:
            loc_anchor = driver.find_element_by_xpath("//h2[contains(text(),'Amazon Pop Up')]").find_element_by_xpath('..')
        except NoSuchElementException:
            continue
            
        location_name = loc_anchor.find_element_by_css_selector('a').text

        cont = loc_anchor.find_elements_by_xpath('p')
        phone_number = cont[1].text
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
