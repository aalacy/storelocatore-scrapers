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
        writer.writerow(["locator_domain", "page_url" , "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    count=0
    data=[]
    driver.get("http://oreganos.com/locations/")
    time.sleep(10)
    stores = driver.find_elements_by_css_selector('div.wpb_column.vc_column_container.vc_col-sm-5.vc_col-md-3 >  div.vc_column-inner > div.wpb_wrapper > div.wpb_text_column.wpb_content_element > div > p > a.color-red')
    name = [stores[i].get_attribute('href') for i in range(0, len(stores))]
    time.sleep(5)
    for i in range(0,len(name)):
            driver.get(name[i])
            time.sleep(5)
            page_url = name[i]
            print("page_url....", page_url)
            try:
                store = driver.execute_script("return wpslMap_0;")
                json_data = store['locations']
                location_name = json_data[0]['store'].replace("&#038;", " ")
                street_addr = json_data[0]['address'] + json_data[0]['address2']
                city = json_data[0]['city']
                state = json_data[0]['state']
                zipcode = json_data[0]['zip']
                lat = json_data[0]['lat']
                lng = json_data[0]['lng']
                store_id = json_data[0]['id']
                phone = driver.find_element_by_css_selector('span.location-phone').text
                hours_of_op = driver.find_element_by_css_selector('div.vc_row.wpb_row.vc_inner.vc_row-fluid.locationBtnRow > div > div > div > div >  div > p').text.split(phone)[1].replace("\n", " ")
                data.append([
                    'http://oreganos.com/',
                    page_url,
                    location_name,
                    street_addr,
                    city,
                    state,
                    zipcode,
                    'US',
                    store_id,
                    phone,
                    '<MISSING>',
                    lat,
                    lng,
                    hours_of_op
                ])
                count+=1
                print(count)
            except:
                pass


    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()