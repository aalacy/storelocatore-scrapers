import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'https://www.elcompadrerestaurant.com/' 
    page_url = 'https://www.elcompadrerestaurant.com/locations'
    r = session.get(page_url, headers = HEADERS)

    soup = BeautifulSoup(r.text, "lxml")
    store_number = ''
    country_code = "US"
    for data in soup.find_all('div', {'class': 'dynamicColumn span6'}):
        
        addr = list(data.find("address").stripped_strings)
        location_name = addr[0]
        street_address = addr[1]
        city = addr[2].split(",")[0]
        state = addr[2].split(",")[-1].split()[0]
        zipp = addr[2].split(",")[-1].split()[-1]

        phone = addr[-2].replace("Phone.","").strip()

        soup1 = BeautifulSoup(session.get(data.find("a",{"id":"ctl01_rptAddresses_ctl00_lnkGetDirection"})['href']).text, "lxml")

        coords = soup1.find(lambda tag: (tag.name == "meta") and "?center" in tag['content'])['content']
        latitude = coords.split("=")[1].split("%2C")[0]
        longitude = coords.split("%2C")[1].split("&")[0]
        if 'Echo Park' in location_name:
            hours = soup.find_all("p",{"class":"fp-el"})[5].text.split("HOURS:")[1].strip()
        else:
            hours = soup.find_all("p",{"class":"fp-el"})[9].text.split("HOURS:")[1].strip()

        
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code, 
                    store_number, phone, 'Restaurant', latitude, longitude, hours, page_url]
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        yield store
  
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
