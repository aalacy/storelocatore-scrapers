import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)
def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def fetch_data():
    data=[]; location_name=[];address_stores=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    #Driver
    driver = get_driver()
    driver.get('http://banditsbbq.com/locations')
    stores=driver.find_elements_by_xpath(("//div[@class='info']"))
    for n in range(0,len(stores)):
        a=stores[n].text.split("\n")
        location_name.append(a[0])
        street_address.append(a[1])
        city.append(a[2].split(",")[0])
        state.append(a[2].split(",")[1].split()[0].strip())
        zipcode.append(a[2].split(",")[1].split()[1].strip())
        phone.append(a[3])
    hours = driver.find_elements_by_class_name('hours')
    for n in range(0,len(hours)):
        hours_of_operation.append(hours[n].text)
    for n in range(0,len(street_address)): 
        data.append([
            'http://banditsbbq.com',
            '<MISSING>',
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            '<MISSING>',
            phone[n],
            '<MISSING>',
            '<MISSING>',
            '<MISSING>',
            hours_of_operation[n]
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
