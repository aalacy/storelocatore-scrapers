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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data=[]
    driver.get("https://www.foxrentacar.com/en/locations.html")
    stores = driver.find_elements_by_css_selector('li.clearfix > a')
    name = [stores[i].get_attribute('href') for i in range(0, len(stores))]
    for i in range(0, len(name)):
        driver.get(name[i])
        time.sleep(5)
        crumb_text = driver.find_element_by_css_selector('#crumb_2 > a > span').text
        if crumb_text == 'Canada' or crumb_text == 'United States':
            street_addr = driver.find_element_by_css_selector('div.loc-address > h5:nth-child(1)').text
            try:
                state_city_zip = driver.find_element_by_css_selector('div.loc-address > h5:nth-child(3)').text
                street_addr = street_addr + " " + driver.find_element_by_css_selector('div.loc-address > h5:nth-child(2)').text
            except:
                state_city_zip = driver.find_element_by_css_selector('div.loc-address > h5:nth-child(2)').text
            if crumb_text == 'United States':
                tagged = usaddress.tag(state_city_zip)[0]
                city = tagged['PlaceName']
                state = tagged['StateName']
                zipcode = tagged['ZipCode']
                country_code = 'US'
            else:
                city = state_city_zip.split(" ")[0]
                state = state_city_zip.split(" ")[1]
                zipcode = state_city_zip.split(" ")[2] + " " + state_city_zip.split(" ")[3]
                country_code ='CA'
            location_name = driver.find_element_by_css_selector('div.margin_bottom > div > h3').text
            phone = driver.find_element_by_xpath("//a[contains(@href, 'tel:')]").text
            hours_of_op = driver.find_element_by_css_selector('div.busines-hours').text

            data.append([
                'https://www.foxrentacar.com/',
                location_name,
                street_addr,
                city,
                state,
                zipcode,
                country_code,
                '<MISSING>',
                phone,
                '<MISSING>',
                '<INACCESSIBLE>',
                '<INACCESSIBLE>',
                hours_of_op
                ])

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()