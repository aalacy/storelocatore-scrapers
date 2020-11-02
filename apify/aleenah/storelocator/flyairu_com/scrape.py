import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('flyairu_com')



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
    res=session.get("https://flyairu.com/")
    soup = BeautifulSoup(res.text, 'html.parser')
    uls = soup.find_all('ul', {'class': 'map-list'})

    for ul in uls:
        page_url+=ul.find_all('a')

    for url in page_url:
        url=url.get('href').strip("/")

        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        try:
            addr = soup.find('address').text.strip().split("\n")
            street = addr[0].strip()
            addr = addr[1].strip().split(",")
            city = addr[0].strip()
            addr = addr[1].strip()
            zip = addr.split(" ")[-1]
            state = addr.replace(zip, "").strip()
            phone = soup.find('div', {'class': 'holder phone'}).text.strip()
            hrlink = url + soup.find('div', {'class': 'holder hours'}).find('a').get('href')
            res = session.get(hrlink)
            soup = BeautifulSoup(res.text, 'html.parser')
            timl = soup.find_all('table', {'class': 'hours_table'})[0].text
            if "Monday:" in timl:
                timl=timl.split("\n")
            else:
                timl = soup.find_all('table', {'class': 'hours_table'})[1].text.split("\n")

        except:
            #only one case http://airu-amarillo.com/ which redirects to a new website
            addr = soup.find('div', {'id': 'text-3'}).text.strip().split("\n")
            street=addr[0]
            phone =addr[2]
            addr=addr[1].split(",")
            city=addr[0]
            addr=addr[1].strip().split(" ")
            state=addr[0]
            zip=addr[1]
            res = session.get("https://ampd.fun/rates/")
            soup = BeautifulSoup(res.text, 'html.parser')
            timl = soup.find_all('div', {'class': 'wpb_wrapper'})[2].text.split("\n")

        logger.info(url)
        tim=""
        for t in timl:

            if "Monday:" in t or "Tuesday:" in t or "Sunday:" in t or "Saturday:" in t or "Friday:" in t or "Thursday:" in t or "Wednesday:"  in t:
                tim+=t+" "

        all.append([
            "https://flyairu.com/",
            url.split("/")[-1].replace(".com","").split("-")[-1].upper(),
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
            tim.strip(),  # timing
            url])

    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
