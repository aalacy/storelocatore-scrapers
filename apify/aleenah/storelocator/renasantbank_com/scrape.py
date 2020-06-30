import csv
from sgrequests import SgRequests
import re
from bs4 import BeautifulSoup

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


    res=session.get("https://locations.renasantbank.com/type/branch/",headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    #print(soup)
    stores = soup.find_all('div', {'class': 'itm-info-wrapper'})
    phones=re.findall(r'<strong>Phone Number</strong>([^<]+)',str(soup),re.DOTALL)
    print(len(phones))
    for store in stores:
        data=store.find('div', {'class': 'info-title-block'})
        loc = data.find('h4').text
        data=str(data.find('p')).replace('</p>','').replace('<p>','').split('<br/>')
        street=data[0]
        data=data[1].split(',')
        city=data[0]
        data=data[1].strip().split(' ')
        state=data[0]
        zip=data[1]
        data=store.find('div', {'class': 'info-info'})
        tim = data.text.split('Hours')[1].strip().replace('\n',', ').replace('M','Mon').replace('F','Fri')
        phone=phones[stores.index(store)].strip()
        all.append([
            "https://renasantbank.com/",
            loc,
            street,
            city,
            state,
            zip,
            'US',
            "<MISSING>",  # store #
            phone,  # phone
            "Branch",  # type
            "<MISSING>",  # lat
            "<MISSING>",  # long
            tim,  # timing
            "https://locations.renasantbank.com/type/branch/"])
    return all

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
