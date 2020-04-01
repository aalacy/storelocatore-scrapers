import csv
from sgrequests import SgRequests
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
    res = session.get("http://jerrysusa.com/locations/")
    soup = BeautifulSoup(res.text, 'html.parser')

    divs = soup.find_all('div', {'class': 'g48'})
    #print(len(divs))
    divs=divs[0::2]
    #print(len(divs))
    del divs[0]
    del divs[-1]
    del divs[-1]
    
    for div in divs:
        #print(div)
        loc=div.find('h4').text
        print(loc)
        ps=div.find_all('p')
        addr=ps[0].text.strip().split("\n")
        if len(addr)==2:
              street=addr[0]
        elif len(addr)==3:
              street=addr[0]+" "+addr[1]
        addr=addr[-1].strip().split(",")
        city=addr[0]
        addr=addr[1].strip().split(" ")
        state=addr[0]
        zip=addr[1]
        phone=ps[1].text.strip()
        if phone=="":
               phone="<MISSING>"



        all.append([
            "http://jerrysusa.com",
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
            "http://jerrysusa.com/locations/"])

    return all

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
