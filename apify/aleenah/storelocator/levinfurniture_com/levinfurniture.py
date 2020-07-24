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

    res=session.get("https://www.levinfurniture.com/api/rest/pages/contacts")
    soup = str(BeautifulSoup(res.text, 'html.parser')).replace('\\t','').replace('\\r\\n','').replace('&lt;\/h3&gt;','').replace('&lt;\/span&gt;','').replace('&lt;\/div&gt;','')
    print(soup)

    #divs = soup.find_all('h3', {'class': 'avb-typography__heading dsg-tools-main-heading dsg-tools-color-primary dsg-tools-fw-bold dsg-contact-3__location-name'})
    locs =re.findall(r'dsg-tools-main-heading="">([^<]*)',soup)
    del locs[0]
    addrs=re.findall(r'address-line\\"\'>([^<]*)<span class=\'\\"dsg-contact-3__address-line\\"\'>([^<]*)',soup)
    geos=re.findall(r'/@(-?[\d\.]+),(-?[\d\.]+)',soup)
    phones=re.findall(r'"tel:([\-\d]+)',soup)

    for i in range(len(phones)):
        #print(locs[i].strip().replace('Mattress: ','').replace(' ','-').replace('\xa0','-'))
        url="https://www.levinfurniture.com/api/rest/pages/locations%2F"+locs[i].strip().replace('Mattress: ','').replace(' ','-').replace('\xa0','-')
        print(url)
        res = session.get(url)
        soup = str(BeautifulSoup(res.text, 'html.parser')).replace('\\t', '').replace('\\r\\n', '').replace('&lt;\/h3&gt;', '').replace('&lt;\/span&gt;', '').replace('&lt;\/div&gt;', '').replace('&lt;\/li&gt;','').replace('&lt;\/ul&gt;','')
        print(soup)
        tim=re.findall(r'"avb-list__item\\"\'>([^<]+)<li class=\'\\"avb-list__item\\"\'>([^<]+)',soup)[0]
        tim=' '.join(tim)
        street=str(addrs[i][0]).strip()
        csz=str(addrs[i][1]).strip().split(',')
        city=csz[0]
        csz=csz[1].strip().split()
        state=csz[0]
        zip=csz[1]

        all.append([
            "https://www.levinfurniture.com",
            locs[i],
            street,
            city,
            state,
            zip,
            "US",
            "<MISSING>",  # store #
            phones[i],  # phone
            "<MISSING>",  # type
            geos[i][0],  # lat
            geos[i][1],  # long
            tim,  # timing
            url])

    return all


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
