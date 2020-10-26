import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re


options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)
#driver2 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver2 = webdriver.Chrome("chromedriver", options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url" , "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)



def parse_geo(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon


def fetch_data():
    # Your scraper here
    data=[]
    count=0
    driver.get("https://www.judesbarbershop.com/location/")
    time.sleep(10)

    stores = driver.find_elements_by_css_selector('li.elementor-icon-list-item > a')
    store1 = driver.find_elements_by_css_selector('h4.elementor-heading-title.elementor-size-default > a')
    names = [stores[i].get_attribute('href') for i in range(0, len(stores))]
    names.append(store1[1].get_attribute('href'))
    location_name = [stores[i].text for i in range(0, len(stores))]
    location_name.append(store1[1].text)

    hours_of_op_general = driver.find_element_by_css_selector('div.elementor-element.elementor-element-7a1824e6.elementor-widget.elementor-widget-text-editor').text
    hours_of_op_cel_north = driver.find_element_by_css_selector('div.elementor-element.elementor-element-66947a9f.elementor-widget.elementor-widget-text-editor').text
    hours_of_op_downtown_lansing = driver.find_element_by_css_selector('div.elementor-element.elementor-element-7c83f86c.elementor-widget.elementor-widget-text-editor').text

    for j in range(0,len(names)):
            print("URL..........." , names[j])
            if 'barbershop/' in names[j]:
                driver2.get(names[j])
                time.sleep(5)
                page_url = names[j]
                address = driver2.find_elements_by_xpath("//a[contains(@href,'https://www.google.com/maps/')]")
                street_addr = address[0].text
                state_city_zip = address[1].text
                zipcode = state_city_zip.split(" ")[-1]
                state = state_city_zip.split(" ")[-2]
                city_list = state_city_zip.split(" ")[:-2]
                if len(city_list) == 1:
                    city = city_list[0]
                else:
                    city = city_list[0] + " " + city_list[1]
                phone = driver2.find_element_by_xpath("//a[contains(@href, 'tel:')]").text
                geomap = driver2.find_element_by_xpath("//a[contains(@href,'https://www.google.com/maps')]").get_attribute('href')
                lat,lon = parse_geo(geomap)
                if location_name[j] == 'Celebration North':
                    hours_of_op = hours_of_op_cel_north
                elif location_name[j] == 'Downtown Lansing':
                    hours_of_op = hours_of_op_downtown_lansing
                else :
                    hours_of_op = hours_of_op_general
                data.append([
                     'https://www.judesbarbershop.com/',
                      page_url,
                      location_name[j],
                      street_addr,
                      city,
                      state,
                      zipcode,
                      'US',
                      '<MISSING>',
                      phone,
                      '<MISSING>',
                      lat,
                      lon,
                      hours_of_op
                    ])
                count+=1
                print(count)
            else:
                pass

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()