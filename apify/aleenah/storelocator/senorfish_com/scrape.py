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

    res=session.get("http://www.xn--seorfish-e3a.com/locations/")
    soup = BeautifulSoup(res.text, 'html.parser')
    urls = soup.find_all('div', {'class': 'fl-rich-text'})
    for url in urls:
        text= re.sub(r'  +','  ',url.text.replace(u'\xa0','').replace('HOURS',"").replace(':','')).split('MAP')[0]
        tim=text.split('  ')[-2]
        text=text.replace(tim,"")
        phone=re.findall(r'[\d\-]+',text)[-1]
        text=text.replace(phone,"").strip()
        zip=re.findall(r'\d{5}',text)
        if zip==[]:
            zip=re.findall(r'(\dOO\d\d)',text)
        zip=zip[-1]
        text=text.replace(zip,"").strip()
        zip=zip.replace('OO','00')
        text=text.split(" ")
        state=text[-1].replace('.','')
        del text[-1]
        text=' '.join(text).split('  ')
        loc=text[0]
        street=text[1]
        city=text[2]

        all.append([
            "http://www.xn--seorfish-e3a.com",
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
            tim,  # timing
            "http://www.xn--seorfish-e3a.com/locations/"])

    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

