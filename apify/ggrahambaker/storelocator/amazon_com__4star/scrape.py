import csv
import os
from sgselenium import SgSelenium
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import usaddress
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('amazon_com__4star')



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
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}
    session = SgRequests()

    locator_domain = 'https://amazon.com/4star'
    loc_url = 'https://www.amazon.com/b/ref=s9_acss_bw_cg_A4S_1a1_w?node=17608448011&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-1&pf_rd_r=65J1BBEFCG70MGVSTQB0&pf_rd_t=101&pf_rd_p=eb3c6053-8d6b-4f16-8e09-b9270e8e27b3&pf_rd_i=17988552011#Amazon4starLocations'
    driver = SgSelenium().chrome()
    driver.get(loc_url)
    driver.implicitly_wait(20)
    hrefs = driver.find_elements_by_xpath("//a[contains(@href, '&pf_rd_m=ATVPDKIKX0DER&pf_rd_s=merchandised-search-6&pf_rd_r')]")

    link_list = []
    for href in hrefs[1:]:
        link = href.get_attribute('href')
        link_list.append(link)

    all_store_data = []
    #logger.info(len(link_list))
    for link in link_list:
        
        driver.get(link)
        driver.implicitly_wait(10)
        
        try:
            loc_anchor = driver.find_element_by_xpath("//h2[contains(text(),'Amazon 4-star')]").find_element_by_xpath('..')
        except:
            try:
                driver.refresh()
                driver.implicitly_wait(10)
                loc_anchor = driver.find_element_by_xpath("//h2[contains(text(),'Amazon 4-star')]").find_element_by_xpath('..')
            except:
                driver.refresh()
                driver.implicitly_wait(10)
                loc_anchor = driver.find_element_by_xpath("//h2[contains(text(),'Amazon 4-star')]").find_element_by_xpath('..')

        location_name = loc_anchor.find_element_by_css_selector('h2').text

        cont = loc_anchor.find_elements_by_xpath('p')
        phone_number = cont[1].text.replace('Phone:', '').strip()
        if phone_number:
            hr_line = cont[2:]
        else:
            phone_number = cont[2].text.replace('Phone:', '').strip()
            hr_line = cont[3:]

        hours = ''
        
        for h in hr_line:
            if 'Regular Hours' in h.text:
                continue
            if 'Holiday' in h.text:
                break
            
            hours += h.text + ' '
        hours = hours.replace("Special hours for those at higher risk due to COVID-19 (65 or older, or with underlying medical conditions):","").strip()

        if 'To come' in phone_number:
            continue            
        
        try:
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
        except:
            lat = '<MISSING>'
            longit = '<MISSING>'

        if lat == '<MISSING>':
            try:
                google_link = cont[0].find_element_by_css_selector('a').get_attribute('href')
                req = session.get(google_link, headers = HEADERS)
                map_link = req.url
                at_pos = map_link.rfind("@")
                lat = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
                longit = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()

                if len(lat) > 20:
                    try:
                        maps = BeautifulSoup(req.text,"lxml")
                        raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
                        lat = raw_gps.split("=")[-1].split(",")[0].strip()
                        longit = raw_gps.split("=")[-1].split(",")[1].strip()
                    except:
                        lat = "<MISSING>"
                        longit = "<MISSING>"
            except:
                lat = '<MISSING>'
                longit = '<MISSING>'

        addy = cont[0].text.replace('Address:', '').strip()

        street_address, city, state, zip_code = parse_addy(addy)
        if "Orchard Center" in city:
            street_address = "4999 Old Orchard Center"
            city = "Skokie"

        if zip_code == "06845":
            zip_code = "06854"

        country_code = 'US'

        page_url = link

        store_number = '<MISSING>'
        location_type = '<MISSING>'
        
        phone_number = phone_number.strip()
        logger.info(phone_number)
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number.encode("ascii", "replace").decode().replace("?",""), location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
