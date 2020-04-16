import csv
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import platform
system = platform.system()
from sgrequests import SgRequests
session = SgRequests()

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    
    if "linux" in system.lower():
        return webdriver.Firefox(executable_path='./geckodriver', options=options)        
    else:
        return webdriver.Firefox(executable_path='geckodriver.exe', options=options)
    
def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    driver = get_driver()
    # addresses = []
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }
    base_url = "https://www.mercyone.org"
    r2 = session.get("https://www.mercyone.org/find-a-location/", headers=headers)
    soup2 = BeautifulSoup(r2.text, "lxml")
    for link in soup2.find("div",{"class":"col-xs-12 col-sm-12 col-md-12 col-lg-12 text-center"}).find_all("a"):
    
        city_url = link['href']+"/location-results"
        if "siouxland" in link['href']:
            city_url = link['href']+"/locations-results"
        else:
            city_url = city_url
        page = 1
        while True:
            driver.get(city_url+"?page="+str(page)+"&count=9")
            soup = BeautifulSoup(driver.page_source, "lxml")
            if soup.find("div",{"class":"ih-field-address-formated"}) == None:
                break
            for data in soup.find("div",{"class":"ih-tab-list ng-scope"}).find_all("div",{"class":"row ng-scope"},recursive=False):
                location_name = data.find("div",{"class":"form-group ih-field-locationnamelink"}).find("div").text
                addr = list(data.find("div",{"class":"ih-field-address-formated"}).stripped_strings)
                street_address = " ".join(addr[:-1]).split("Suite")[0].strip()
                city = addr[-1].split(",")[0]
                state = " ".join(addr[-1].split(",")[1].split(" ")[:-1])
                zipp = addr[-1].split(",")[1].split(" ")[-1]
                phone = data.find("div",{"class":"form-group ih-field-locationphone"}).text.strip()
                page_url = base_url+data.find("div",{"class":"form-group ih-field-locationnamelink"}).find("a")['href']
                # print(page_url)
                driver.get(page_url)
                soup1 = BeautifulSoup(driver.page_source, "lxml")
                try:
                    json_data = json.loads(soup1.find("script",{"class":"ng-binding"}).text.split("var ih_jsonLocationDetail=")[1].replace("};","}"))
                    latitude = json_data['Latitude']
                    longitude = json_data['Longitude']
                    store_number = json_data['Id']
                    if json_data['OrgUnitTypes']:
                        location_type = json_data['OrgUnitTypes'][0]['OrgUnitTypeName']
                    else:
                        location_type = "<MISSING>"
                except:
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                    store_number = "<MISSING>"
                    location_type = "<MISSING>"
                try:
                    hours = " ".join(list(soup1.find("div",{"class":"form-group ih-field-locationhours"}).stripped_strings)).replace("Hours of Operation","")
                except:
                    hours = "<MISSING>"
                store = []
                store.append(base_url)
                store.append(location_name)
                store.append(street_address.replace("Floor",""))
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append("US")
                store.append(store_number)
                store.append(phone)
                store.append(location_type)
                store.append(latitude)
                store.append(longitude)
                store.append(hours)
                store.append(page_url)
                
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                # print("data == "+str(store))
                # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                yield store
            page+=1
  
        
            
def scrape():

    data = fetch_data()
    write_output(data)

scrape()
