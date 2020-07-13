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

    res=session.get("https://desertfitnessaz.com/locations/")
    soup = BeautifulSoup(res.text, 'html.parser')
    divs = soup.find_all('section', {'class': 'l-section wpb_row height_auto'})
    for div in divs:
        url ="https://desertfitnessaz.com"+div.find('h2').find('a').get('href')
        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        divi = soup.find_all('div', {'class': 'wpb_wrapper'})
        data=divi[2].text.strip().replace('\n\n\n','\n').split('\n')
        loc=data[0]
        addr=data[4].split(',')
        sz=addr[-1].strip().split(' ')
        state=sz[0]
        zip=sz[1]
        del addr[-1]
        city = addr[-1].strip()
        del addr[-1]
        street=', '.join(addr)
        phone=data[5]
        tim =divi[10].text.replace('Gym Hours','').replace('\n\n\n','\n').replace('\n',' ').strip()
        lat,long=re.findall(r'LatLng\((-?[\d\.]+), (-?[\d\.]+)\)',str(soup))[0]
        all.append([
            "https://desertfitnessaz.com",
            loc,
            street,
            city,
            state,
            zip,
            "US",
            "<MISSING>",  # store #
            phone,  # phone
            "<MISSING>",  # type
            lat,  # lat
            long,  # long
            tim,  # timing
            "https://desertfitnessaz.com/locations/"])
    return all

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
