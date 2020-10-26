import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('shoppersdrugmart_ca')



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
    page_url=[]
    res=session.get("https://stores.shoppersdrugmart.ca/en/listing/")
    soup = BeautifulSoup(res.text, 'html.parser')
    sa = soup.find_all('a', {'class': 'strloc-allstr-store-link'})
    logger.info(len(sa))
    for a in sa:
        url=a.get('href')
        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        #jso = soup.find_all('script', {'type': 'application/ld+json'})[1].text
        logger.info(url)
        #logger.info(jso.text)
        #jso=json.loads(jso.text)

        loc=soup.find('h1').text
        #logger.info(loc)
        addr=soup.find('p', {'class': 'store-details__address'}).text.strip().split("\n")
        street=addr[0].strip()
        addr=addr[1].strip().split(",")
        city=addr[0]
        addr=addr[1].strip().split(" ")
        state=addr[0]
        zip = soup.find('p', {'class': 'store-details__address'}).text.replace(street, '').replace(city, '').replace(state, '').replace(',', '').strip()

        """tim=re.findall(r'"openingHours": \[([^\]]+)',jso)[0].replace("[","").replace("]","").strip().strip(",").replace('"','').split(",")
        if len(tim)==6:
            tim.append("Sunday Closed")
        elif len(tim)==5:
            tim.append("Saturday Closed")
            tim.append("Sunday Closed")
        elif len(tim)<5:
            logger.info("errrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrfrrrrrrrrrrrrrrrrrrrrrrrrrr")
        
        tim=" ".join(tim).replace("Mo","Monday").replace("Tu","Tuesday").replace("We","Wednesday").replace("Th","Thursday").replace("Fr","Friday").replace("Sa","Saturday").replace("Su","Sunday")

"""

        tds=soup.find('table', {'class': 'table table-sm'}).find_all('td')
        tim=""
        for td in tds:
            tim+=td.text.strip()+" "
        #logger.info(tim)
        phone=soup.find('a', {'class': 'phone'}).text
        """phone=re.findall(r'"telephone": "([^"]+)',jso)[0]
        street=re.findall(r'"streetAddress": "([^"]+)',jso)[0]
        city=re.findall(r'"addressLocality": "([^"]+)',jso)[0]
        state=re.findall(r'"addressRegion": "([^"]+)',jso)[0]
        country=re.findall(r'"addressCountry": "([^"]+)',jso)[0]"""
        coord=soup.find('div', {'id': 'map'})
        lat=coord.get('data-lat')
        long=coord.get('data-lng')
        id=soup.find('p', {'class': 'store-number'}).text.split("#")[-1]
        type=""
        atags=soup.find('div', {'id': 'nav-tab'}).find_all('a')
        for at in atags:
            type+=at.text+", "
        type=type.strip().strip(",")
        all.append([
            "https://shoppersdrugmart.ca/",
            loc,
            street,
            city,
            state,
            zip,
            'CA',
            id,  # store #
            phone,  # phone
            type,  # type
            lat,  # lat
            long,  # long
            tim.strip(),  # timing
            url])

    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

