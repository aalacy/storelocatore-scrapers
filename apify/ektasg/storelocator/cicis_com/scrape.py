import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)



def get_info(driver):
    location_name = driver.find_element_by_css_selector('h1.c-location-title').text
    print("location name" , location_name)
    try:
        street_addr = driver.find_element_by_css_selector('span.c-address-street.c-address-street-1').text + " " + driver.find_element_by_css_selector('span.c-address-street.c-address-street-2').text
    except:
        street_addr = driver.find_element_by_css_selector('span.c-address-street.c-address-street-1').text
    city = driver.find_element_by_css_selector('span.c-address-city').text
    state = driver.find_element_by_css_selector('span.c-address-state').text
    zipcode = driver.find_element_by_css_selector('span.c-address-postal-code').text
    phone = driver.find_element_by_css_selector('span.c-phone-number-span.c-phone-main-number-span').text
    hours_of_op = driver.find_element_by_css_selector('table.c-location-hours-details').text
    latitude = driver.find_element_by_css_selector('span.coordinates > meta:nth-child(1)').get_attribute('content')
    longitude = driver.find_element_by_css_selector('span.coordinates > meta:nth-child(2)').get_attribute('content')
    return location_name, street_addr, city, state, zipcode, phone, hours_of_op, latitude, longitude


def fetch_data():
    # Your scraper here
    count=0
    data=[]
    driver.get("https://www.cicis.com/locations/index.html")
    time.sleep(10)
    stores = driver.find_elements_by_css_selector('a.c-directory-list-content-item-link')
    name = [stores[i].get_attribute('href') for i in range(0, len(stores))]
    time.sleep(5)
    for i in range(len(name)):
            driver.get(name[i])
            page_url = name[i]
            time.sleep(5)
            stores1 = driver.find_elements_by_css_selector('a.c-directory-list-content-item-link')
            if stores1 == []:
                try:
                    print("inside first if first try:    " , page_url)
                    location_name, street_addr, city, state, zipcode, phone, hours_of_op, latitude, longitude = get_info(
                        driver)
                    data.append([
                        'https://www.cicis.com/',
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
                        latitude,
                        longitude,
                        hours_of_op
                    ])
                    count = count + 1
                    print(count)
                except:
                    locations = driver.find_elements_by_css_selector('a.location-link.location-link-site')
                    locations_names = [locations[i].get_attribute('href') for i in range(0, len(locations))]
                    for i in range(0, len(locations_names)):
                        driver.get(locations_names[i])
                        page_url = locations_names[i]
                        print("inside first if first except :     " , page_url)
                        time.sleep(5)
                        location_name, street_addr, city, state, zipcode, phone, hours_of_op, latitude, longitude = get_info(
                            driver)
                        data.append([
                            'https://www.cicis.com/',
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
                            latitude,
                            longitude,
                            hours_of_op
                        ])
                        count = count + 1
                        print(count)
            else:
                name_sub = [stores1[i].get_attribute('href') for i in range(0, len(stores1))]
                for i in range(0,len(name_sub)):
                    driver.get(name_sub[i])
                    page_url = name_sub[i]
                    time.sleep(5)
                    try:
                        print("inside else second try :     ", page_url)
                        location_name, street_addr, city, state, zipcode, phone, hours_of_op, latitude, longitude = get_info(driver)
                        data.append([
                            'https://www.cicis.com/',
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
                            latitude,
                            longitude,
                            hours_of_op
                        ])
                        count = count + 1
                        print(count)
                    except:
                        print("inside else second except :     ", page_url)
                        #location_name = driver.find_element_by_css_selector('h1.page-title').text
                        locations = driver.find_elements_by_css_selector('a.location-link.location-link-site')
                        locations_names = [locations[i].get_attribute('href') for i in range(0, len(locations))]
                        for i in range(0,len(locations_names)):
                            driver.get(locations_names[i])
                            page_url = locations_names[i]
                            time.sleep(5)
                            print(page_url)
                            location_name, street_addr, city, state, zipcode, phone, hours_of_op, latitude, longitude = get_info(driver)
                            data.append([
                                'https://www.cicis.com/',
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
                                latitude,
                                longitude,
                                hours_of_op
                            ])
                            count = count + 1
                            print(count)


    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()