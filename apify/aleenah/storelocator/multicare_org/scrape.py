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
all = []

def fetch_data():
    # Your scraper here
    res = session.get("https://www.multicare.org/all-locations/")
    soup = BeautifulSoup(res.text, 'html.parser')
    div= soup.find('div', {'class': 'rtecontent location_list clearfix'})
    lis = div.find_all('li')
    print(len(lis))
    for li in lis:
        id=li.find('div', {'class': 'location_item linky'}).get('data-location_id')
        loc= li.find('h2', {'class': 'title'}).text.strip()
        print(loc)
        div=li.find('div', {'class': 'text'})
        ps=div.find_all('p')
        tim="<MISSING>"
        phone="<MISSING>"
        for p in ps:
            data= p.text
            if "Address" in data:
                #print(p)
                addr=str(p).split('<a')[0].split('</b><br/>')[1].replace('<br>','\n').replace('<br/>','\n')
                addr=addr.replace('Address','').replace(',,',',').strip().split('\n')

                #print(addr)
                sz=addr[-1].strip().split(',')
                city=sz[0]
                sz=sz[1].strip().split(' ')
                state=sz[0]
                try:
                    zip=sz[1]
                except:
                    zip="<MISSING>"
                del addr[-1]
                street=' '.join(addr)
            elif "Hours:" in data:
                tim = data.replace('Hours:','').strip().replace('\n',' ')
            elif "Phone Number:" in data:
                phone=data.replace('Phone Number:','').strip()
                if phone=="":
                    phone="<MISSING>"

        all.append([
            "https://www.multicare.org",
            loc.replace('\u200b',''),
            street.replace('\u200b',''),
            city.replace('\u200b',''),
            state.replace('\u200b',''),
            zip.replace('\u200b',''),
            "US",
            id.replace('\u200b',''),  # store #
            phone.replace('\u200b',''),  # phone
            "<MISSING>",  # type
            "<MISSING>",  # lat
            "<MISSING>",  # long
            tim.replace('\u200b',''),  # timing
            "https://www.multicare.org/all-locations/"])

    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()