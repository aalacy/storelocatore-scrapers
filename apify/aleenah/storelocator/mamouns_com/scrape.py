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

    res=session.get("https://mamouns.com/locations")
    soup = BeautifulSoup(res.text, 'html.parser')
    ps = soup.find_all('div', {'class': 'details'})
    latlongs= re.findall(r'"latlong":\[{"latitude":"(-?[\d\.]+)","longitude":"(-?[\d\.]+)"}]',str(soup))
    for p in ps:


        loc = p.find('div', {'class': 'title'}).text
        url = 'https://mamouns.com/locations/' + loc.split(',')[0].strip().replace(' ','-')
        if 'COMING SOON' in loc:
            continue
        data=p.find('div', {'class': 'copy'}).find_all('p')
        street,city,state,zip=re.findall(r'<a .*>(.*)<br/>(.*), (.*) ([\d]{5})</a>',str(data[0]))[0]
        tim= data[1].text.replace('pm','pm ').replace('am','am ').replace('  ',' ').strip()
        if len(data)==3:
            phone = data[2].text
            if 'N/A' in phone:
                phone="<MISSING>"
        else:
            phone="<MISSING>"


        all.append([
            "https://mamouns.com",
            loc,
            street,
            city,
            state.strip(),
            zip,
            "US",
            "<MISSING>",  # store #
            phone,  # phone
            "<MISSING>",  # type
            latlongs[ps.index(p)][0],  # lat
            latlongs[ps.index(p)][1],  # long
            tim,  # timing
            url])

    return all

def scrape():
    data = fetch_data()
    write_output(data)


scrape()