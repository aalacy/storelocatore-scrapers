import csv
import requests
from bs4 import BeautifulSoup
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('getmacd_com')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states=[]
    cities = []
    types=[]
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids=[]
    page_url=[]
    countries=[]

    res =  requests.get("https://getmacd.com/")
    soup = BeautifulSoup(res.text, 'html.parser')
    #logger.info(soup)
    div = soup.find('div', {'id': 'location-section'})
    #for div in divs:
    divs=div.find_all('div', {'class': 'col sqs-col-4 span-4'})
    logger.info(len(divs))
    for div in divs:
        page_url.append("https://getmacd.com"+div.find('a').get('href'))

    for url in page_url:
        res=requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        div = soup.find('div', {'class': 'sqs-block-content'})
        locs.append(div.find('h2').text.strip())
        data=soup.find('div', {'class': 'sqs-block map-block sqs-block-map sized vsize-12'}).get('data-block-json')
        street.append(re.findall(r'"addressLine1":"([^"]+)",',data)[0])
        addr=re.findall(r'"addressLine2":"([^"]+)",',data)[0].split(",")
        zips.append(addr[2].strip())
        states.append(addr[1].strip())
        cities.append(addr[0].strip())
        lat.append(re.findall(r'"mapLat":([\d\.]+),', data)[0])
        long.append(re.findall(r'"mapLng":(-?[\d\.]+),', data)[0])
        ps=div.find_all("p")
        ph=re.findall(r'Phone: ([\d\)\( \-\.]+)',ps[0].text)
        if ph==[]:
            ph = re.findall(r'Phone: ([\d\)\( \-\.]+)', ps[1].text)
            if ph==[]:
                ph="<MISSING>"
            else:
                ph=ph[0].strip()
        else:
            ph=ph[0].strip()
        phones.append(ph)
        tim = ps[1].text
        if ph in tim:
            tim=re.findall(r'Phone: [\d\)\( \-\.]+(.*)', tim)[0]
        tim =" ".join(re.findall(r'[A-Z][^A-Z]*',tim))
        timing.append(tim)

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://getmacd.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])  # timing
        row.append(page_url[i])  # page url

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
