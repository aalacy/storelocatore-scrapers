import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addressesess = []
    base_url = "https://www.avera.org"
    r = session.get("https://www.avera.org/locations/search-results/?sort=13&page=1")
    soup = BeautifulSoup(r.text, "lxml")
    for number in soup.find("select",{"class":"SuperShort"}).find_all("option"):
        #print(number.text)
        r1 = session.get("https://www.avera.org/locations/search-results/?searchId=fb3e969c-8b80-ea11-a82e-000d3a611c21&sort=13&page="+str(number.text))
        soup1 = BeautifulSoup(r1.text, "lxml")
        for url in soup1.find("div",{"class":"LocationsList"}).find_all("li"):
            link = 'https://www.avera.org/locations'+url.find("a",{"class":"Name"})['href'].replace("..","")
            if "&id" in link:
                store_number = link.split("&id=")[-1]
            else:
                store_number = "<MISSING>"
            r2 = session.get(link)
            soup2 = BeautifulSoup(r2.text, "lxml")
            try:
                data = json.loads(soup2.find("script",{"type":"application/ld+json"}).text)
                location_name = data['name']
                street_address = data['address']['streetAddress'].split("Suite")[0].replace(",","").split("Ste")[0].replace("Second Floor","").replace("3rd Floor","").replace("2nd Floor","").replace("4th Floor - Plaza 2","")
                city = data['address']['addressLocality']
                state = data['address']['addressRegion']
                zipp = data['address']['postalCode']
                phone = data['telephone']
                latitude = data['geo']['latitude']
                longitude = data['geo']['longitude']
                page_url = data['url']
                if soup2.find("div",{"class":"Hours"}):
                    hours = " ".join(list(soup2.find("div",{"class":"Hours"}).stripped_strings)).replace("Hours of Operation","")
                else:
                    hours = "<MISSING>"
            except:
                pass
        
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append(store_number)
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(hours)
            store.append(page_url)
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            if store[2] in addressesess:
                continue
            addressesess.append(store[2])

            # print("data == "+str(store))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
