import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

session = SgRequests()
def fetch_data():

    all=[]
    res = session.get("http://greshampetroleum.com/locations.php")
    soup = BeautifulSoup(res.text, 'html.parser')
    data = soup.find_all('table')[4].find_all('td')[4]

    hs=data.find_all('h3')
    ps=data.find_all('p')[0::2]
    print(len(ps))

    for h in range(len(hs)):
        loc=hs[h].text.strip()
        #print(loc)
        p=ps[h].text.replace("|","").replace('\xa0','').replace('\r','').strip().split('\n')
        street=p[0]
        phone=p[-1]
        del p[0]
        del p[-1]
        if len(p) ==1:
            sz=p[0].strip().split(",")
        else:

            sz = p[1].strip().split(",")

        city = sz[0]
        sz = sz[1].strip().split(" ")
        state = sz[0]
        zip = sz[1].split("-")[0]

        all.append([
            "http://greshampetroleum.com",
            loc,
            street,
            city,
            state,
            zip,
            "US",
            "<MISSING>",  # store #
            phone,  # phone
            "<MISSING>",  # type
            "<MISSING>",  # lat
            "<MISSING>",  # long
            "<MISSING>",  # timing
            "http://greshampetroleum.com/locations.php"])

    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()