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
    res=session.get("https://www.7forallmankind.com/store-locator/")
    soup = BeautifulSoup(res.text, 'html.parser')
    urls = soup.find('ul', {'id': 'list-store-detail'}).find_all('h3')
    print(len(urls))
    for url in urls:
        url=url.find('a').get('href')
        #print(url)
        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        div = soup.find('div', {'class': 'store-info'})
        loc=div.find('h4').text
        addr=div.find('p', {'class': 'address-store'}).text
        zip=addr.split("-")[-1].strip()
        if ", United States. " in addr:
            cont="US"
            addr = addr.split(", United States. ")[0].strip()
        elif ", Canada. " in addr:
            cont="CA"
            addr = addr.split(", Canada. ")[0].strip()
        add=addr.split(",")
        state=add[-1]
        city=add[-2]
        street=addr.replace(state,"").replace(city,"").strip().strip(",")
        phone=div.find_all('a')
        if phone!=[]:
            phone=phone[0].text
        else:
            phone="<MISSING>"
        tim=re.sub(r'[ ]+',' ',soup.find('div', {'class': 'table-responsive'}).text.replace('\n',' '))
        #print(tim)

        lat,long=re.findall(r'{lat:(.*),lng:(.*),name:',str(soup))[0]
        all.append([
            "https://www.7forallmankind.com",
            loc,
            street,
            city,
            state,
            zip,
            cont,
            "<MISSING>",  # store #
            phone,  # phone
            "<MISSING>",  # type
            lat,  # lat
            long,  # long
            tim.strip(),  # timing
            url])
    return(all)

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
