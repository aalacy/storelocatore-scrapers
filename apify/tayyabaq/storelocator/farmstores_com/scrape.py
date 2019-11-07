import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, time, requests
from bs4 import BeautifulSoup

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
    data=[]; location_name=[];store_no=[]; city=[];street_address=[]; zipcode=[]; state=[]; latitude=[]; longitude=[]; hours_of_operation=[]; phone=[]
    r = requests.get('http://www.farmstores.com/locations/')
    soup = BeautifulSoup(r.content, 'html.parser')
    script = soup.findAll('script')
    lat=re.findall(r'\>","[\d.*]*\","',str(script))
    lon = re.findall(r'\","-[\d.*]*\"',str(script)) 
    driver = get_driver()
    driver.get('http://www.farmstores.com/locations/')
    time.sleep(3)
    loc = driver.find_elements_by_class_name('loc-title')
    location = [loc[n].text for n in range(0,len(loc))]
    stores = driver.find_elements_by_class_name('location-address')
    hour = driver.find_elements_by_class_name('location')
    hours = [hour[n].text for n in range(0,len(hour))]
    for n in range(0,len(stores)-1):
        if 'COMING SOON' not in location[n]: 
            try:
                city.append(stores[n].text.split(",")[1])
                street_address.append(stores[n].text.split(",")[0])
                state.append(stores[n].text.split(",")[2].split()[0])
                zipcode.append(stores[n].text.split(",")[2].split()[1])
            except:
                street_address.append(stores[n].text.split("ave")[0]+' ave')
                city.append(stores[n].text.split()[-3])
                state.append(stores[n].text.split()[-2])
                zipcode.append(stores[n].text.split()[-1])
            location_name.append(location[n])
            latitude.append(lat[n].replace('>","','').replace('","',""))
            longitude.append(lon[n].replace('","',"").replace('"',""))
            try:
                store_no.append(location[n].split("(")[1].replace(")",""))
            except:
                store_no.append("<MISSING>")
            if 'Hours' in hours[n]:
                hours_of_operation.append(str("Hours: "+hours[n].split("Hours:")[1]))
            else:
                hours_of_operation.append("<MISSING>")
            if 'Phone:' in hours[n]:
                phone.append(str("Phone: "+hours[n].split("Phone:")[1].split("Hours:")[0].strip()))
            else:
                phone.append("<MISSING>")
    for n in range(0,len(street_address)): 
        data.append([
            'https://www.farmstores.com',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            store_no[n],
            phone[n],
            '<MISSING>',
            latitude[n],
            longitude[n],
            hours_of_operation[n]
        ])
    driver.quit()
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
