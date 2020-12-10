import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('toddpilates_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://www.toddpilates.com"
    r = session.get("https://www.toddpilates.com/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    location_url = []
    for location in soup.find_all("nav",{'class':"w-dropdown-list"})[-1].find_all("a"):
        name = location.text.strip()
        # logger.info(base_url + location['href'])
        location_request = session.get(base_url + location['href'], headers=headers)

        location_soup = BeautifulSoup(location_request.text, "lxml")
        yelp_url = location_soup.find("a", {"href": re.compile("yelp.com")})["href"]
        page_url = yelp_url
        # logger.info(page_url)
        yelp_request = session.get(yelp_url, headers=headers)
        yelp_soup = BeautifulSoup(yelp_request.text, "html5lib")
        jd = yelp_soup.find_all('script', text = re.compile('address'), attrs = {'type' : 'application/ld+json'})[0]
        # logger.info(jd)
        location_details = json.loads(jd.text)
        section = yelp_soup.find_all("section", class_="lemon--section__373c0__fNwDM margin-t4__373c0__1TRkQ padding-t4__373c0__3hVZ3 border--top__373c0__3gXLy border-color--default__373c0__3-ifU")[3]
        # logger.info(section)
        listsection = list(section.stripped_strings)
        hours = " ".join(listsection).split("Get directions")[1].replace("Edit business info", "").strip()
        geo = section.find("img")['src'].split("center=")[1].split("&")[0]
        latitude = geo.split("%2C")[0].strip()
        longitude = geo.split("%2C")[-1].strip()
        # logger.info(latitude, longitude)

        store = []
        store.append("https://www.toddpilates.com")
        store.append(location_details["name"].replace("&amp;","&"))
        store.append(location_details["address"]["streetAddress"].replace("\n", ","))
        store.append(location_details["address"]["addressLocality"])
        store.append(location_details["address"]["addressRegion"])
        store.append(location_details["address"]["postalCode"])
        store.append(location_details["address"]["addressCountry"])
        store.append("<MISSING>")
        store.append(
            location_details["telephone"] if location_details["telephone"] else "<MISSING>")
        store.append("tod pilates & barre")
        store.append(latitude)
        store.append(longitude)
        store.append(hours)
        store.append(page_url)
        store = [x.strip() if type(x) == str else x for x in store]
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
