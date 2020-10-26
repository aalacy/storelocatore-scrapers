import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re

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
all=[]
def fetch_data():
    # Your scraper here

    res=session.get("https://www.abchome.com/content/locations")
    soup = BeautifulSoup(res.text, 'html.parser')
    divs = soup.find_all('div', {'class': 'locations'})
    for div in divs:
        if "flagship" in div.find('a').get('href'):
            type = "Flagship"
        else:
            type = "<MISSING>"
        loc =div.find('div', {'class': 'locations__title'}).text.strip()
        data = div.find_all('div', {'class': 'contact-wrapper__details'})
        addr=data[0].find_all('p')
        #print(addr)
        street=addr[0].text
        cs=addr[1].text.strip().split(',')
        city = cs[0].strip()
        state = cs[1]
        zip=addr[2].text
        phone=data[1].text.strip()
        tim=""
        ps =data[2].find_all('p')
        for p in ps:
            tim+= p.text.strip()+" "
        tim=tim.strip().replace('\n',' ')

        all.append([
            "https://www.abchome.com",
            loc,
            street,
            city,
            state.strip(),
            zip,
            "US",
            "<MISSING>",  # store #
            phone,  # phone
            type,  # type
            "<MISSING>",  # lat
            "<MISSING>",  # long
            tim,  # timing
            "https://www.abchome.com/content/locations"])
    return all

def scrape():
    data = fetch_data()
    write_output(data)


scrape()

