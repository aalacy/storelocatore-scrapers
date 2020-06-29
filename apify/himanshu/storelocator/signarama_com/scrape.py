import csv
import requests
from bs4 import BeautifulSoup as bs
import re
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import platform
system = platform.system()



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
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    driver = get_driver()
    url=['https://signarama.com/location/usa/alabama/', 'https://signarama.com/location/usa/arizona/', 'https://signarama.com/location/usa/arkansas/', 'https://signarama.com/location/usa/california/', 'https://signarama.com/location/usa/colorado/', 'https://signarama.com/location/usa/connecticut/', 'https://signarama.com/location/usa/delaware/', 'https://signarama.com/location/usa/florida/', 'https://signarama.com/location/usa/georgia/', 'https://signarama.com/location/usa/hawaii/', 'https://signarama.com/location/usa/illinois/', 'https://signarama.com/location/usa/indiana/', 'https://signarama.com/location/usa/iowa/', 'https://signarama.com/location/usa/kentucky/', 'https://signarama.com/location/usa/louisiana/', 'https://signarama.com/location/usa/maine/', 'https://signarama.com/location/usa/maryland/', 'https://signarama.com/location/usa/massachusetts/', 'https://signarama.com/location/usa/michigan/', 'https://signarama.com/location/usa/minnesota/', 'https://signarama.com/location/usa/missouri/', 'https://signarama.com/location/usa/nevada/', 'https://signarama.com/location/usa/new-hampshire/', 'https://signarama.com/location/usa/new-jersey/', 'https://signarama.com/location/usa/new-mexico/', 'https://signarama.com/location/usa/new-york/', 'https://signarama.com/location/usa/north-carolina/', 'https://signarama.com/location/usa/north-dakota/', 'https://signarama.com/location/usa/ohio/', 'https://signarama.com/location/usa/oklahoma/', 'https://signarama.com/location/usa/pennsylvania/', 'https://signarama.com/location/usa/rhode-island/', 'https://signarama.com/location/usa/south-carolina/', 'https://signarama.com/location/usa/south-dakota/', 'https://signarama.com/location/usa/tennessee/', 'https://signarama.com/location/usa/texas/', 'https://signarama.com/location/usa/utah/', 'https://signarama.com/location/usa/vermont/', 'https://signarama.com/location/usa/virginia/', 'https://signarama.com/location/usa/washington/', 'https://signarama.com/location/usa/washington-dc/', 'https://signarama.com/location/usa/wisconsin/']
    return_main_object = []
    base_url = "https://signarama.com/"
    list1=[]
    for tag in url:
        driver.get(tag)
        soup1 = bs(driver.page_source,'lxml')
        for d in soup1.find_all("div",{"class":"col-lg-3 p-1 my-3"}):
            phone = list(d.stripped_strings)[-2]
            # print(phone)
            city = list(d.stripped_strings)[-3].split(',')[0]
            state =list(d.stripped_strings)[-3].split(',')[1].strip().split(" ")[0]
            zipp = list(d.stripped_strings)[-3].split(',')[1].strip().split(" ")[1]
            street_address = " ".join(list(d.find_all("p",{'class':"m-0"})[-1].stripped_strings)[:-1])
            name = d.find_all("a")[0].find("amp-img")['alt'].replace("Signarama ",'')
            page_url ="https://signarama.com"+d.find("a")['href']
            driver.get(page_url)
            soup3 = bs(driver.page_source,'lxml')
            # soup3 = bs(requests.get(page_url).text,'lxml')
            # print(soup3)
            lat=''
            lng =''
            try:
                lat = soup3.find("amp-img",{"src":re.compile("https://maps.googleapis.com/maps/api")})['src'].split("=")[1].split("%2C")[0]
                lng=(soup3.find("amp-img",{"src":re.compile("https://maps.googleapis.com/maps/api")})['src'].split("=")[1].split("%2C")[1].split("&")[0])
            except:
                lat="<MISSING>"
                lng = "<MISSING>"
            store = []
            store.append(base_url)
            store.append(name.encode('ascii', 'ignore').decode('ascii').strip())
            store.append(street_address.encode('ascii', 'ignore').decode('ascii').strip())
            store.append(city.encode('ascii', 'ignore').decode('ascii').strip())
            store.append(state.encode('ascii', 'ignore').decode('ascii').strip())
            store.append(zipp)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(lat.strip() if lat.strip() else "<MISSING>" )
            store.append(lng.strip() if lng.strip() else "<MISSING>")
            store.append( "<MISSING>")
            store.append(page_url)
            # store = [x.replace("–", "-") if type(x) ==
            #          str else x for x in store]
            store = [x.encode('ascii', 'ignore').decode(
                'ascii').strip() if type(x) == str else x for x in store]
            # print("data ===" + str(store))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~")
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
