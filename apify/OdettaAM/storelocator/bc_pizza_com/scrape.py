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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)



def parse_hours(str):
    bad_chars = ['&lt;', 'table' , 'class="wpsl-opening-hours"', 'role="presentation"', '\/time&gt;\/td&gt;\/tr&gt;tr&gt;td&gt;','\/td&gt;td&gt;time&gt;', '!&lt;\/td&gt;&lt;td&gt;&lt;time&gt;', '\/time&gt;\/td&gt;\/tr&gt;\/table&gt;', '&gt;tr&gt;td&gt;', '&lt;\/time&gt;&lt;\/td&gt;&lt;\/tr&gt;&lt;tr&gt;&lt;td&gt;','\/td&gt;','td&gt;','Closed','\/td&gt;','\/tr&gt;','\/table','&gt;','\/time','\/' ,'&gt;\/td&gt;\/tr&gt;\/&gt;']
    for i in bad_chars:
        str = str.replace(i, '')
    return str



def fetch_data():
    # Your scraper here
    data=[]
    driver.get("https://bc.pizza/wp-admin/admin-ajax.php?action=store_search&lat=44.314844&lng=-85.60236399999997&max_results=100&search_radius=500")
    time.sleep(5)
    page = driver.page_source
    page = page.split('[')[1].split(']')[0]
    stores = eval(page)
    for i in range(len(stores)):
        location_name = stores[i]['store']
        street_address = stores[i]['address'] + " " + stores[i]['address2']
        city = stores[i]['city']
        state = stores[i]['state']
        zipcode = stores[i]['zip']
        phone = stores[i]['phone']
        store_number = stores[i]['id']
        latitude = stores[i]['lat']
        longitude = stores[i]['lng']
        hours_of_op = stores[i]['hours']
        hours_of_op = parse_hours(hours_of_op)
        data.append([
            'https://bc.pizza/',
            location_name,
            street_address,
            city,
            state,
            zipcode,
            'US',
            store_number,
            phone,
            '<MISSING>',
            latitude,
            longitude,
            hours_of_op
        ])

    time.sleep(3)
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()