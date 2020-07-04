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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://fcer.com"
    r = session.get(base_url+"/locations")
    soup = BeautifulSoup(r.text,"lxml")
    
   
    for location in soup.find_all('a',{"class":"inline-block mt-4 py-4 px-6 uppercase tracking-wide font-bold bg-blue-600 hover:bg-blue-700 text-white text-center w-full"}):
        
        page_url = base_url+location['href']
        r1 = session.get(session.get(page_url).url.replace("https://firsttexashospitalcyfair.com","https://firsttexashospitalcyfair.com/hospital"))
    
        soup1= BeautifulSoup(r1.text,"lxml")
        
        name = location.parent.parent.find("div",{"class":re.compile("font-bold text-2xl")}).get_text()
        main1=json.loads(soup1.find('script',{'type':"application/ld+json"}).text)

        store=[]
        store.append("https://fcer.com")
        store.append(name)
        store.append(main1['address']['streetAddress'])
        store.append(main1['address']['addressLocality'])
        store.append(main1['address']['addressRegion'])
        store.append(main1['address']['postalCode'])
        store.append('US')
        store.append("<MISSING>")
        store.append(main1['telephone'])
        store.append("<MISSING>")
        store.append(main1['geo']['latitude'])
        store.append(main1['geo']['longitude'])
        store.append(main1['openingHours'].replace("Mo-Su","Open 24 Hours"))
        store.append(page_url)
        yield store
    

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
