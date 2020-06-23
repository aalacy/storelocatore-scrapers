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
    driver.get(
        "https://signarama.com/location/")
    s = requests.Session()
    cookies_list = driver.get_cookies()
    cookies_json = {}
    for cookie in cookies_list:
        cookies_json[cookie['name']] = cookie['value']
    cookies_string = str(cookies_json).replace("{", "").replace("}", "").replace("'", "").replace(": ", "=").replace(
        ",", ";")
    kp = cookies_string
    news2 = str(kp).split( )[-2]+" _fbp=fb.1.1592806746301.1420733007; "+kp.split( )[-1]+'; '+kp.split( )[0]+" sucuri_cloudproxy_uuid_305525f9b=44dbc42e1263d648bf758fba9816a9fd; sucuri_cloudproxy_uuid_127ef07d9=447667094fb7d3236b5160ffe6d8878c; sucuri_cloudproxy_uuid_dbb23d1d5=6be6fcc15dbdb40c610ca8cd0e8b1e2c; sar_url=ri-north-kingstown"
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'cookie': str(news2),
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'
    }
    return_main_object = []
    base_url = "https://signarama.com/"
    soup = bs(requests.get("https://signarama.com/location/locator.php?q=", headers=headers).text,'lxml')
    for tag in soup.find("div",{"class":"locations"}).find_all("a"):
        soup1 = bs(requests.get("https://signarama.com"+tag['href'], headers=headers).text,'lxml')
        for d in soup1.find_all("div",{"class":"col-lg-3 p-1 my-3"}):
            phone = list(d.stripped_strings)[-2]
            city = list(d.stripped_strings)[-3].split(',')[0]
            state =list(d.stripped_strings)[-3].split(',')[1].strip().split(" ")[0]
            zipp = list(d.stripped_strings)[-3].split(',')[1].strip().split(" ")[1]
            street_address = " ".join(list(d.find_all("p",{'class':"m-0"})[-1].stripped_strings)[:-1])
            name = d.find_all("a")[0].find("amp-img")['alt'].replace("Signarama ",'')
            page_url ="https://signarama.com"+d.find("a")['href']
            soup3 = bs(requests.get(page_url, headers=headers).text,'lxml')
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
