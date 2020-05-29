import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

session = SgRequests()
def fetch_data():

    all=[]
    res = session.get("https://www.git-n-go.com/our-locations/")
    soup = BeautifulSoup(res.text, 'html.parser')
    stores = soup.find('ul', {'class': 'location-list'}).find_all('li')
    for store in stores:
        data=store.text.strip().split("\n")
        loc=data[0].strip()

        street=data[0].strip().split(" ")
        id=street[0].replace("#","")
        del street[0]
        street=" ".join(street)
        sz=data[1].strip().split(",")
        city=sz[0]
        sz=sz[1].strip().split(" ")
        state=sz[0]
        zip=sz[1].split("-")[0]
        phone=data[2].strip()

        all.append([
            "https://www.git-n-go.com",
            loc,
            street,
            city,
            state,
            zip,
            "US",
            id,  # store #
            phone,  # phone
            "<MISSING>",  # type
            "<MISSING>",  # lat
            "<MISSING>",  # long
            "<MISSING>",  # timing
            "https://www.git-n-go.com/our-locations/"])

    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()