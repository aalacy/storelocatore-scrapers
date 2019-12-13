import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
import re

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--disable-plugins")
options.add_argument( "--no-experiments")
options.add_argument( "--disk-cache-dir=null")

#driver = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver = webdriver.Chrome("chromedriver", options=options)
#driver1 = webdriver.Chrome("C:\chromedriver.exe", options=options)
driver1 = webdriver.Chrome("chromedriver", options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def parse_geo(url):
    try:
        lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    except:
        lon ='<MISSING>'
    try:
        lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    except:
        lat='<MISSING>'
    return lat, lon

def fetch_data():
    data=[]
    driver.get("https://www.firsthorizon.com/Support/Contact-Us/Location-Listing")
    page_url = "https://www.firsthorizon.com/Support/Contact-Us/Location-Listing"
    li=[]
    abc=driver.find_elements_by_xpath("//div[@class='ftb-listing-item__content']//ul")
    for i in abc:
        k=i.get_attribute('innerText').splitlines()
        hours =""
        for m in range(len(k)):
            hours = hours + " " + k[m].lstrip()
        li.append(hours)

    maps=[]
    adress=[]
    abc=driver.find_elements_by_xpath("//div[@class='ftb-listing-item__content']//a[@target='_blank']")
    for i in abc:
        k=i.get_attribute('href')
        k1=i.get_attribute('textContent')
        #k=k.replace('\n','')
        maps.append(k)
        adress.append(k1)
    
    state=[]
    zipcode=[]
    street=[]
    city=[]
    lat=[]
    lng=[]
    phone = []
    phone_nos = driver.find_elements_by_xpath("//div[@class='ftb-listing-item__content']//a[@class='ftb-listing-item__content-spacer']")
    name = []
    loc_names = driver.find_elements_by_xpath("//div[@class='ftb-listing-item__title ftb-color--abbey']")
    for i in range(len(adress)):
        addr = adress[i].splitlines()
        state.append(addr[2].split(',')[1].split(" ")[-2])
        zipcode.append(addr[2].split(',')[1].split(" ")[-1])
        street.append(addr[1].lstrip())
        city.append(addr[2].split(',')[0].lstrip())
        ph = phone_nos[i].get_attribute('innerText')
        phone.append(ph)
        lc_name = loc_names[i].get_attribute('innerText')
        name.append(lc_name)
        driver1.get(maps[i])
        time.sleep(5)
        l,ln = parse_geo(driver1.current_url)
        lat.append(l)
        lng.append(ln)
        name1 = name[i]
        street1 = street[i]
        state1 = state[i]
        zipcode1 = zipcode[i]
        city1 = city[i]
        try:
            lat1 = lat[i]
            lng1 = lng[i]
        except:
            pass
        try:
            country1 = 'US'
        except:
            pass
        phone1 = phone[i]
        try:
            hour1 = li[i]
        except:
            pass

        data.append([
            'https://www.firsthorizon.com/',
            page_url,
            name1,
            street1,
            city1,
            state1,
            zipcode1,
            country1,
            '<MISSING>',
            phone1,
            '<MISSING>',
            lat1,
            lng1,
            hour1
        ])

    time.sleep(3)
    driver.quit()
    driver1.quit()
    return data


def scrape():
        data = fetch_data()
        write_output(data)
    
scrape()
