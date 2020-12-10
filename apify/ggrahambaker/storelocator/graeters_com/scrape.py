import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.graeters.com/'
    ext = 'stores/locations-list'

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    req = session.get(locator_domain+ext, headers = HEADERS)
    base = BeautifulSoup(req.text,"lxml")

    hrefs = base.find(class_="column main").find_all("a")
    link_list = []
    for a in hrefs:
        href = a['href']
        if "retail-stores/" in href:
            street = str(a).split('> ')[1].split(",")[0]
            link_list.append([locator_domain+"stores/"+href, street])

    all_store_data = []

    for link_row in link_list:
        link = link_row[0]
        req = session.get(link, headers = HEADERS)
        base = BeautifulSoup(req.text,"lxml")

        coords = base.find(class_="location-button action primary")["href"].split("/")[-1].split(",")

        lat = coords[0]
        longit = coords[1]

        phone_number = base.find(class_="location-phone").text.strip()

        location_name = base.h1.text.strip()

        street_address = link_row[1].replace("Towne","Town").replace("W. ","West ").replace("E. ","East ").replace("N. ","North ").replace("S. ","South ").replace("147 Easton","142 Easton")
        if street_address == "6509 Bardstown Road":
            city = "Louisville"
            state = "KY"
            zip_code = "40291"
        else:
            addy = base.find(class_="location-address").text.replace("Hwy","Highway").replace("Pike","Pk").replace(" St "," Street ").replace(" Rd "," Road ").replace("N. ","North ").replace(" S. "," South ").replace(" W High"," West High").replace(".,","").replace(street_address,"").strip()

            if addy[:1] == "," or addy[:1] == ".":
                addy = addy[1:].strip()
            city, state, zip_code = addy_ext(addy)

        if city == "Suite 116 Beachwood":
            city = "Beachwood"
            street_address = street_address + " Suite 116"

        hours = " ".join(list(base.find(class_="widget block block-static-block").ul.stripped_strings)).replace("Temporarily No Bakery","").strip()

        country_code = 'US'
        page_url = link
        store_number = '<MISSING>'
        location_type = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
