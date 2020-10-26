import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import usaddress


options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url" , "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data=[]
    count=0
    driver.get("https://paninikabobgrill.com/our-locations/#")
    stores = driver.find_elements_by_css_selector('#locations-list > li')
    page_url = "https://paninikabobgrill.com/our-locations/#"
    for store in stores:
        location_name = store.find_element_by_css_selector('div.location-address').get_attribute('data-location')
        print(location_name)
        if location_name == 'coming-soon':
            pass
        else:
            info = store.text.splitlines()
            lat = store.find_element_by_css_selector('div.location-address').get_attribute('data-lat')
            lng = store.find_element_by_css_selector('div.location-address').get_attribute('data-lng')
            address = info[1]
            tagged = usaddress.tag(address)[0]
            try:
                street_addr = tagged['AddressNumber'] + " " + \
                              tagged['StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]+ " " + \
                              tagged['OccupancyType'] + " " + tagged['OccupancyIdentifier']
            except:
                try:
                    street_addr = tagged['AddressNumber'] + " " + tagged['StreetNamePreDirectional'] + " " + tagged[
                        'StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
                except:
                    try:
                        street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + \
                                      tagged['OccupancyType'].split('\n')[0] + " " + tagged['OccupancyIdentifier']
                    except:
                        try:
                            street_addr = tagged['AddressNumber'] + " " + tagged['StreetNamePreDirectional'] + " " + \
                                          tagged[
                                              'StreetName'] + " " + tagged['StreetNamePostType'].split('\n')[0]
                        except:
                            try:
                                street_addr = tagged['AddressNumber'] + " " + tagged['StreetNamePreDirectional'] + " " + \
                                              tagged['StreetName'] + " " + \
                                              tagged['StreetNamePostType'].split('\n')[0] + " " + \
                                                tagged['OccupancyType'] + " " + tagged['OccupancyIdentifier']
                            except:
                                try:
                                    street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + \
                                                  tagged['StreetNamePostType'].split('\n')[0] + " " + \
                                                  tagged['OccupancyIdentifier'].split('\n')[0]
                                except:
                                    try:
                                        street_addr = tagged['AddressNumber'] + " " + tagged['StreetName'] + " " + \
                                                      tagged['StreetNamePostType'].split('\n')[0]
                                    except:
                                        try:
                                            street_addr = tagged['AddressNumber'] + " " + tagged[
                                                'StreetNamePreType'] + " " + tagged['StreetName'] + " " + tagged[
                                                              'StreetNamePostDirectional']
                                        except:
                                            try:
                                                street_addr = tagged['AddressNumber'] + " " + tagged['StreetName']
                                            except:
                                                street_addr = '<MISSING>'
            state = tagged['StateName']
            city = tagged['PlaceName']
            zipcode = tagged['ZipCode']
            phone = info[2]
            hours_of_op = info[3] +" " + info[4]
            data.append([
                 'https://paninikabobgrill.com/',
                  page_url,
                  location_name,
                  street_addr,
                  city,
                  state,
                  zipcode,
                  'US',
                  '<MISSING>',
                  phone,
                  '<MISSING>',
                  lat,
                  lng,
                  hours_of_op
                ])
            count+=1
            print(count)

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()