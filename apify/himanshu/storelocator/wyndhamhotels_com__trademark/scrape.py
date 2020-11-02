import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time 

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def request_wrapper(url,method,headers,data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = session.get(url,headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    elif method == "post":
        while True:
            try:
                if data:
                    r = session.post(url,headers=headers,data=data)
                else:
                    r = session.post(url,headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    else:
        return None
def fetch_data():
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Connection': 'keep-alive',
    }
    base_url = "https://www.wyndhamhotels.com"
    location_url1 = "https://www.wyndhamhotels.com/en-uk/trademark/locations"
    try:
        r = session.get(location_url1, headers=headers,  allow_redirects=False)
    except Exception as e :
        pass
    soup= BeautifulSoup(r.text,"lxml")
    a = soup.find("div",{"class":"aem-rendered-content"}).find_all("div",{"class":"state-container"})[0:20]
    for y in a:
        e = (y.find_all("li",{"class":"property"}))
        for b in e:
            k = (b.find('a')['href'])
            location_url = base_url+k
            try:
                r1 = session.get(location_url, headers=headers,  allow_redirects=False)
            except Exception as e:
                pass
            soup1= BeautifulSoup(r1.text,"lxml")
            b = soup1.find("script",{"type":"application/ld+json"})
            if b != [] and b != None:
                h  = json.loads(b.text)  
                location_name = (h['name'])
                street_address = h['address']["streetAddress"]              
                latitude = h['geo']["latitude"]      
                longitude = h['geo']["longitude"]                 
                city = h['address']["addressLocality"]   
                if "postalCode" in  h['address'] :   
                    zipp = h['address']["postalCode"]
                else:
                    zipp = "<MISSING>"
                ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zipp))
                us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp))
                if ca_zip_list:
                    zipp = ca_zip_list[-1]
                    country_code = "CA"
                if us_zip_list:
                    zipp = us_zip_list[-1]
                    country_code = "US"
                if len(zipp)==6 or len(zipp)==7:
                    country_code = "CA"
                else:
                    country_code = "US"
                if  "addressRegion" in h['address']:
                    state = h['address']["addressRegion"]
                else:
                    state = "<MISSING>"
                phone = h['telephone']              
                store = []
                store.append("https://www.wyndhamhotels.com/en-uk/trademark")
                store.append(location_name if location_name else "<MISSING>") 
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append(country_code)
                store.append("<MISSING>") 
                store.append(phone.replace('-','') if phone else "<MISSING>" )
                store.append("<MISSING>")
                store.append( latitude if latitude else "<MISSING>")
                store.append( longitude if longitude else "<MISSING>")
                store.append("<MISSING>")
                store.append(location_url)
                if store[2] in addresses :
                    continue
                addresses.append(store[2])
                yield store
    a1 = soup.find("div",{"class":"aem-rendered-content"}).find_all("div",{"class":"state-container"})[20:25]
    for y1 in a1:
        e1 = (y1.find_all("li",{"class":"property"}))
        for b1 in e1:
            k1 = (b1.find('a')['href'])
            location_url = base_url+k1
            try:
                r2 = session.get(location_url, headers=headers,  allow_redirects=False)
            except Exception as e:
                pass
            soup1= BeautifulSoup(r2.text,"lxml")
            b1 = soup1.find("script",{"type":"application/ld+json"})
            if b1 != [] and b1 != None:
                h1  = json.loads(b1.text)  
                location_name = (h1['name'])
                street_address = h1['address']["streetAddress"]              
                latitude = h1['geo']["latitude"]      
                longitude = h1['geo']["longitude"]                 
                city = h1['address']["addressLocality"]  
                if "postalCode" in  h1['address']  :  
                    zipp = h1['address']["postalCode"]
                else:
                    zipp = "<MISSING>"         
                ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zipp))
                us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp))
                if ca_zip_list:
                    zipp = ca_zip_list[-1]
                    country_code = "CA"
                if us_zip_list:
                    zipp = us_zip_list[-1]
                    country_code = "US"
                if len(zipp)==6 or len(zipp)==7:
                    country_code = "CA"
                else:
                    country_code = "US"
                if  "addressRegion" in  h1['address']:
                    state = h1['address']["addressRegion"]
                else:
                    state = "<MISSING>"
                phone = h1['telephone']              
                store = []
                store.append("https://www.wyndhamhotels.com/en-ca/trademark")
                store.append(location_name if location_name else "<MISSING>") 
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append(country_code)
                store.append("<MISSING>") 
                store.append(phone.replace('-','') if phone else "<MISSING>" )
                store.append("<MISSING>")
                store.append( latitude if latitude else "<MISSING>")
                store.append( longitude if longitude else "<MISSING>")
                store.append("<MISSING>")
                store.append(location_url)
                if store[2] in addresses :
                    continue
                addresses.append(store[2])
                yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
