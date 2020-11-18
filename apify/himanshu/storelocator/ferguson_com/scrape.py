import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addresses = []
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }   
    base_url = "https://www.ferguson.com"    
    r = session.get("https://www.ferguson.com/searchBranch", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
   
    for i in soup.find_all("a", {"class":"state_area"}):
        href = "https://www.ferguson.com/branchResults?state="+str(i.text)+"&distance=50"
        r1 = session.get(href, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        loc_link = soup1.find_all('a', class_='button tertiary middle')
        for link in loc_link:  
            r2 = session.get(base_url + link['href'], headers= headers)
            soup2 = BeautifulSoup(r2.text, "lxml")
            try:
                data = json.loads(soup2.find("div", {"id":"locations"}).text)
            except:
                pass
            for i in data['locationInfo']['locationBusinessList']:
                page_url = "https://www.ferguson.com/branch/"+ i['branchPageURL']
                if "https://www.ferguson.com/branch/morrisville-nc-industrial" in page_url or "https://www.ferguson.com/branch/richmond-va-industrial" in page_url :
                    # duplicate data
                    pass

                else:
                    page_url = page_url
                    street_address = data['locationInfo']['addressLine1']+" "+data['locationInfo']['addressLine2']
                    city = data['locationInfo']['city']
                    state = data['locationInfo']['state']       
                    zipp = data['locationInfo']['zip']
                    country_code = data['locationInfo']['country']            
                    latitude = data['locationInfo']['latitude']
                    longitude = data['locationInfo']['longitude']
                    location_type = i['locationType']
                    phone = i['phone'].replace('BATH','').strip()
                    store_number = i['id']
                    hours_of_operation = i['hours'].replace("|",'')
                    location_name = i['branchName']
                    page_url = "https://www.ferguson.com/branch/"+ i['branchPageURL']


                    store = []
                    store.append(base_url)
                    store.append(location_name)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(zipp)
                    store.append(country_code)
                    store.append(store_number) 
                    store.append(phone if phone else "<MISSING>")
                    store.append(location_type)
                    store.append(latitude if latitude else "<MISSING>")
                    store.append(longitude if longitude else "<MISSING>")
                    store.append(hours_of_operation if hours_of_operation else "<MISSING>")
                    store.append(page_url)
                    
                    if store[-1] in addresses:
                        continue
                    addresses.append(store[-1])
                    store = [x.strip() if x else "<MISSING>" for x in store]
                    yield store
        
                
def scrape():
    data = fetch_data()
    write_output(data)

scrape()

