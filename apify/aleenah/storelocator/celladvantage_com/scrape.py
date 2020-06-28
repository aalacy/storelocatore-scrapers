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

    res=session.get("http://celladvantage.com/uscellular-locations.html")
    soup = BeautifulSoup(res.text, 'html.parser')
    divs = soup.find_all('div', {'id': 'location_pic'})

    for div in divs:
        url ="http://celladvantage.com/" +div.find('a').get('href')
        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        stores = soup.find_all('div', {'id': 'location_address'})
        titles=soup.find_all('div', {'id': 'location_title'})
        pics=soup.find_all('div', {'id': 'location_pic'})
        for s in range(len(stores)):
            street,city,state,zip=re.findall(r'<h5>(.*)<br/>(.*), (.*) ([\d]{5})',str(stores[s]))[0]
            #print(stores[s])
            loc,phone=re.findall('<h5>(.*)</h5>(.*)</p>',str(titles[s]))[0]
            loc=loc.replace('♦','')
            coord=re.findall(r'll=(-?[\d\.]+),(-?[\d\.]+)',pics[s].find('a').get('href'))
            if coord==[]:
                coord = re.findall(r'/@(-?[\d\.]+),(-?[\d\.]+)', pics[s].find('a').get('href'))
                if coord==[]:
                    lat=long="<MISSING>"
            else:
                lat=coord[0][0]
                long=coord[0][1]
            all.append([
                "http://celladvantage.com/",
                loc,
                street,
                city,
                state,
                zip,
                'US',
                "<MISSING>",  # store #
                phone,  # phone
                "<MISSING>",  # type
                lat,  # lat
                long,  # long
                "<MISSING>",  # timing
                url])

    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
