import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


session = SgRequests()


def fetch_data():
    # Your scraper here
    
    page_url = []

    res=session.get("https://www.dollartree.com/locations/")
    soup = BeautifulSoup(res.text, 'html.parser')
    sls = soup.find('div', {'class': 'content_area'}).find_all('a')
    print("sls: ",len(sls))
    count=0
    for sl in sls:
        res = session.get(sl.get('href'))
        #print(sl.get('href'))
        soup = BeautifulSoup(res.text, 'html.parser')
        cls = soup.find('div', {'class': 'content_area'}).find_all('a')
        #print("cls",len(cls))
        for cl in cls:
            res = session.get(cl.get('href'))
            #print(cl.get('href'))
            soup = BeautifulSoup(res.text, 'html.parser')
            pls = soup.find_all('div', {'class': 'storeinfo_div '})
            #print("pls: ",len(pls))
            for p in pls:
                p=p.find('a')
                page_url.append(p.get('href'))
                count+=1
                #print(p.get('href'))
    print("count: ",count)  
    all =[]
    for url in page_url:
        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        data = soup.find_all('script', {'type': 'application/ld+json'})[1].contents
        js=json.loads("".join(data))
        addr=js["address"]
        timl=js["openingHoursSpecification"]
        tim=""
        for l in timl:
            tim+= l["dayOfWeek"]+": "+l["opens"]+" - "+l["closes"]+" "
        
        all.append([
        "https://www.dollartree.com/",
        js["ContainedIn"],
        addr["streetAddress"],
        addr["addressLocality"],
        addr["addressRegion"],
        addr["postalCode"].split("-")[0],
        addr["addressCountry"],
        js["@id"], 
        js["telephone"],  
        js["@type"],  
        js["geo"]["latitude"], 
        js["geo"]["longitude"], 
        tim.strip(),  
        url])
        
    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
