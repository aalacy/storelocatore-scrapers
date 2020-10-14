import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
import sgzip


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8", newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.thepodhotel.com"

    soup = bs(session.get("https://www.thepodhotel.com/locations.html",headers=headers).text,"lxml")
    results = json.loads(soup.find(lambda tag:(tag.name == "script") and "var locations =" in tag.text).text.split("var locations =")[1].split("var snazzystyle")[0].replace("];","]").replace("'",'"'))
    
    for result in results:

        location_name = result[0]
        lat = result[1]
        lng = result[2]

        street_address = result[3].split(",")[0]
        if "," in result[4]:
            city = result[4].split(",")[1].strip()
            state = result[4].split(",")[-1].split()[0]
            zipp = result[4].split(",")[-1].split()[1]
        else:
            city = result[4].split()[0]
            state = result[4].split()[1]
            zipp = result[4].split()[2]

        
        page_url = "https://www.thepodhotel.com/"+str(location_name.replace("POD BK","pod-brooklyn").replace(" ","-").lower())+"/"
        
        if "pod-brooklyn" in page_url:

            contact_url = page_url + "contact.html"
        else:
            contact_url = page_url + "contact-us.html"

        contact_soup = bs(session.get(contact_url).text, "lxml")
        try:
            phone = contact_soup.find("a",{"href":re.compile("tel:")})['href'].split("tel:")[1].strip()
        except:
            phone = "<MISSING>"
    
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append("<MISSING>")
        store.append(page_url)
        
        yield store
       

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

