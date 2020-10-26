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
    headers={
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
'accept-encoding': 'gzip, deflate',
'accept-language': 'en-US,en;q=0.9',
'cache-control': 'max-age=0',
'sec-fetch-dest': 'document',
'sec-fetch-mode': 'navigate',
'sec-fetch-site': 'none',
'sec-fetch-user': '?1',
'upgrade-insecure-requests': '1',
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
    }
    res=session.get("https://www.rhodes101.com/locations/",headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    #print(soup)
    stores = soup.find('div', {'class': 'et_pb_row et_pb_row_1 location-row et_pb_gutters2'}).find_all('div', {'class': 'et_pb_text_inner'})

    for store in stores:
        loc = store.find('h4').text.strip()

        p=str(store.find('p')).replace('\xa0','').split('</a>')[0]

        data=re.findall(r'<p>(.*),<br/>(.*), (.*) <span class="zip">(.*)</span><br/>.*<a href="tel:(.*)">',p)

        if data ==[]:
           data=re.findall(r'<p>(.*),<br/>(.*), (.*) <span class="zip">(.*)<br/></span>.*<a href="tel:(.*)">',p)

        if data ==[]:
            data= re.findall(r'<p>(.*), (.*), (.*) <span class="zip">(.*)</span><br/>.*<a href="tel:(.*)">',p)

        if data ==[]:
            data = re.findall(r'<p>(.*), (.*), (.*) <span class="zip">(.*)<br/></span>.*<a href="tel:(.*)">',p)


        street, city, state,zip,phone= data[0]
        all.append([
            "https://www.rhodes101.com",
            loc,
            street,
            city,
            state,
            zip,
            'US',
            "<MISSING>",  # store #
            phone,  # phone
            "<MISSING>",  # type
            "<MISSING>",  # lat
            "<MISSING>",  # long
            "<MISSING>",  # timing
            "https://www.rhodes101.com/locations/"])
    return all
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
