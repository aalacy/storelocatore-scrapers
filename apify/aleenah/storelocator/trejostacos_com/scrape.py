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
    page_url=[]
    res=session.get("https://www.trejostacos.com/")
    soup = BeautifulSoup(res.text, 'html.parser')
    urls = soup.find('div', {'data-controller-folder': 'locations'}).find_all('a')


    for url in urls:
        url = "https://www.trejostacos.com"+url.get('href')
        print(url)
        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        loc = soup.find('h1').text.strip()
        if "429 Too Many Requests" in loc:
            res = session.get(url)
            soup = BeautifulSoup(res.text, 'html.parser')
            loc = soup.find('h1').text.strip()
        h2s=soup.find_all('h2')
        """try:
            coord=h2s[0].find('a').get('href')
            lat,long= re.findall(r'/@(-?[\d\.]+),(-?[\d\.]+)',coord)[0]
        except:
            """
        coord = soup.find('div', {'class': 'sqs-block map-block sqs-block-map sized vsize-12'}).get('data-block-json')
        #print(coord)
        #street=re.findall(r'"addressLine1":"([^"]+)"',coord)[0]
        #csz=re.findall(r'"addressLine2":"([^"]+)"',coord)[0].split(',')
        #city=csz[0].strip()
        #state=csz[1].strip()
        #zip=csz[2].strip()
        lat =re.findall(r'"markerLat":(-?[\d\.]+)',coord)[0]
        long = re.findall(r'"markerLng":(-?[\d\.]+)',coord)[0]
        try:
            phone=h2s[0].find_all('a')[1].text
        except:
            phone="<MISSING>"
        #print(str(h2s[0]))
        street,city,sz=re.findall(r'>(.*)<br/>(.*),(.*)</a>',str(h2s[0]))[0]
       # print(str(h2s[0]))
        sz=sz.strip().split(" ")
        state=sz[0]
        zip=sz[1].replace('</a><br/><a','')
        street =street.split('>')[-1]
        #print(street, city, phone)
        tim=h2s[1].text.replace('DAY','DAY ').replace('  ',' ')
        print(tim)

        all.append([
                "https://www.trejostacos.com",
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
                tim,  # timing
                url])

    return all

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
