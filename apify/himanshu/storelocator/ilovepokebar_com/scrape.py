import csv
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('ilovepokebar_com')


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
    r = session.get("https://www.ilovepokebar.com/locations")
    locator_domain = "https://www.ilovepokebar.com"
    soup = BeautifulSoup(r.text, "lxml")
    for data in soup.find_all("div",{"class":"mini-location-module"}):
        location_name = data.find("h4",{"class":"location-module-subheader"}).text.strip()
        street_address = data.find("div", {"class":"subtext-block"}).text
        city = data.find("div", {"class":"address-text-block"}).text.replace("El Paso TX 79932","El Paso, TX 79932").split(",")[0]
        if "New Zealand" in data.find("div", {"class":"address-text-block"}).text:
            continue
        state = data.find("div", {"class":"address-text-block"}).text.strip().replace("â"," ").replace("El Paso TX 79932","El Paso, TX 79932").split(",")[1].split(" ")[1].replace("\x80\x88","")
        zipp = " ".join(data.find("div", {"class":"address-text-block"}).text.strip().replace("â"," ").replace("El Paso TX 79932","El Paso, TX 79932").split(",")[1].split(" ")[2:]).replace("V5T3J2","V5T 3J2").replace("\x80\x88","")
        if len(zipp) == 5:
            country_code = "US"
        else:
            country_code = "CA"
        if data.find("a", {"class":"phone-link"}) != None:
            phone = data.find("a", {"class":"phone-link"})['href'].replace("tel:","").strip().replace("#","<MISSING>")
        else:
            phone = "<MISSING>"
        
        page_url =locator_domain+data.find("a",{"class":"text-link-button w-button"})['href']

    
        store = []
        store.append(locator_domain)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append(country_code)
        store.append("<MISSING>") 
        store.append(phone)
        store.append("Fast-Food")
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append("<MISSING>")
        store.append(page_url)
        

        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
        # logger.info("data ===="+str(store))

        yield store 

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
