import csv
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgrequests import SgRequests
from random import choice
import http.client
import re
import json
import sgzip
import ssl
import urllib3


session = SgRequests()

session = SgRequests()
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    #print("Error##################")
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context
def get_proxy():
    url = "https://www.sslproxies.org/"
    r = session.get(url)
    soup = BeautifulSoup(r.content, "html5lib")
    return {'https': (choice(list(map(lambda x:x[0]+':'+x[1],list(zip(map(lambda x:x.text,soup.findAll('td')[::8]),map(lambda x:x.text,soup.findAll('td')[1::8])))))))}

def proxy_request(request_type, url, **kwargs):
    while 1:
        try:
            proxy = get_proxy()
            #print("Using Proxy {}".format(proxy))
            
            r = requests.request(request_type, url, proxies=proxy, timeout=3, **kwargs)
            if "CMSSiteMapList" not in r.text:
                continue
            else:
              break
        except:
            pass
    return r
def proxy_request1(request_type, url, **kwargs):
    while 1:
        try:
            proxy = get_proxy()
            #print("Using Proxy {}".format(proxy))
            
            r = requests.request(request_type, url, proxies=proxy, timeout=3, **kwargs)
            if "channel-content full-width" not in r.text:
                continue
            else:
                break
        except:
            pass
    return r
def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url", ])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    
    urllib3.disable_warnings()
    base_url = "https://www.wawa.com"
   
    
    # r = proxy_request("get","https://www.wawa.com/site-map", verify=False, headers=headers)
    # r = session.get(page_url, headers=r_headers, verify=False)
    session = requests.Session()
    response = session.get("https://www.wawa.com/site-map",verify= False)
    cookies_json = session.cookies.get_dict()
    cookies_string = str(cookies_json).replace("{", "").replace("}", "").replace("'", "").replace(": ", "=").replace(",", ";")
    # print(cookies_string)
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
    'Content-Type': 'application/json',
    'Cookie': cookies_string,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' 
    }
    r = proxy_request("get","https://www.wawa.com/site-map", verify=False, headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    # print(soup.prettify())
    addresses = []
    for link in soup.find_all("ul",{"class":"CMSSiteMapList"})[-1].find_all("a",{"class":"CMSSiteMapLink"}):
        locator_domain = base_url
        store_number = link['href'].split("/")[2]
        page_url = base_url + link['href']
        r = session.get(page_url,verify= False,headers = headers)
        cookies_json = session.cookies.get_dict()
        cookies_string = str(cookies_json).replace("{", "").replace("}", "").replace("'", "").replace(": ", "=").replace(",", ";")
        # print(cookies_string)
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'Content-Type': 'application/json',
        'Cookie': cookies_string,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' 
        }
        r = proxy_request1("get",page_url, verify=False, headers=headers)
        soup = BeautifulSoup(r.text,"lxml")
        location_name = soup.find("span",{"itemprop":"name"}).text.strip()
       # print(location_name)
        try:
            street_address = soup.find("span",{"itemprop":"streetAddress"}).text.strip()
        except:
            street_address ="<MISSING>"
        try:
            city = soup.find("span",{"itemprop":"addressLocality"}).text.strip()
        except:
            city:"<MISSING>"
        try:
            state = soup.find("span",{"itemprop":"addressRegion"}).text.strip()
        except:
            state= "<MISSING>"
        try:
            zipp = soup.find("span",{"itemprop":"postalCode"}).text.strip()
        except:
            zipp = "<MISSING>"
        try:
            phone = soup.find("span",{"itemprop":"telephone"}).text.replace("Phone Number:","").strip()
        except:
            phone = "<MISSING>"
        try:
            hours_of_operation = soup.find("meta",{"itemprop":"openinghours"})["content"]
        except:
            hours_of_operation = "<MISSING>"
        country_code="US"
        try:
            latitude = soup.find("meta",{"itemprop":"latitude"})["content"]
            longitue = soup.find("meta",{"itemprop":"longitude"})["content"]
        except:
            latitude="<MISSING>"
            longitue= "<MISSING>"
        location_type = "<MISSING>"
        store_number= location_name.split("#")[-1].strip()
        store = [locator_domain, location_name.encode('ascii', 'ignore').decode('ascii').strip(), street_address.encode('ascii', 'ignore').decode('ascii').strip(), city.encode('ascii', 'ignore').decode('ascii').strip(), state.encode('ascii', 'ignore').decode('ascii').strip(), zipp.encode('ascii', 'ignore').decode('ascii').strip(), country_code,
                        store_number, phone.encode('ascii', 'ignore').decode('ascii').strip(), location_type, latitude, longitue, hours_of_operation.replace("Hours:", "").encode('ascii', 'ignore').decode('ascii').strip(), page_url]

        if str(store[2]) + str(store[-1]) not in addresses:
            addresses.append(str(store[2]) + str(store[-1]))
            store = [x if x else "<MISSING>" for x in store]
            #print("data = " + str(store))
            #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store

    
    
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
