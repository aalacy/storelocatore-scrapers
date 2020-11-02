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
    driver = get_driver()
    driver.get('http://houseofjoychinese.com/')
    location = driver.find_elements_by_xpath('//div[contains(@id,"sidebar")]/p')
    street_address = [location[n].text.split("\n")[2] for n in range(0,len(location))]
    location_name = [str(location[n].text.split("\n")[0]+" "+location[n].text.split("\n")[1]) for n in range(0,len(location))]
    city = [location[n].text.split("\n")[3].split(",")[0] for n in range(0,len(location))]
    state = [location[n].text.split("\n")[3].split(",")[1].split()[0].strip() for n in range(0,len(location))]
    zipcode =[location[n].text.split("\n")[3].split(",")[1].split()[1].strip() for n in range(0,len(location))] 
    phone = [location[n].text.split("\n")[-1] for n in range(0,len(location))] 
    for n in range(0,len(street_address)): 
        data.append([
            'http://houseofjoychinese.com',
            location_name[n],
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
            '<MISSING>'
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
