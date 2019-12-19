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
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
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

    titles=[]
    names=[]
    driver.get("https://imxpilates.com/studios.php")
    stores = driver.find_elements_by_xpath("//div[contains(@class,'studionewcol')]//p//a[contains(@href,'http://')]")
    for i in range(0,len(stores)):
       if "coming soon" not in stores[i].text.lower() :
        names.append(stores[i].get_attribute('href'))
        titles.append(stores[i].text )
    
    
    print(len(names))
    print(len(titles))
    count =0
    for j in range(len(names)):
        #print(names[j])
        #print(titles[j])
        #if "coming soon" in titles[j].lower():
        #    print("contnued")
        #    continue
        driver.get(names[j])
        time.sleep(5)
        #print("time")
        page_url = names[j]
        try:
            location_name = driver.current_url.split("branchname=")[1]
        except:
            location_name = driver.current_url.split("branches/")[1]
        text = driver.find_element_by_css_selector('div.footer-logo > p').text.splitlines()
        street_address = text[0]
        state_city_zip = text[1]
        zipcode = state_city_zip.split(" ")[-1]
        state = state_city_zip.split(" ")[-2]
        city = state_city_zip.split(",")[0]
        phone = text[3]
        #store_id = driver.find_element_by_partial_link_text('Buy Classes').get_attribute('href').split('studioid=')[1].split('&')[0]
        store_id = driver.find_element_by_xpath("//a[contains(@href,'studioid=')]").get_attribute('href').split('studioid=')[1].split('&')[0]
        geomap = driver.find_element_by_css_selector('div.footer-logo > p > a:nth-child(8)').get_attribute('href')
        driver2.get(geomap)
        time.sleep(5)
        lat,lon = parse_geo(driver2.current_url)
        data.append([
             'https://imxpilates.com/',
              page_url,
              location_name,
              street_address,
              city,
              state,
              zipcode,
              'US',
              store_id,
              phone,
              '<MISSING>',
              lat,
              lon,
              '<MISSING>'
            ])
        count+=1
        print(count)

    time.sleep(3)
    driver.quit()
    driver2.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
