import csv
import json
import time
import random
import threading
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from concurrent.futures import ThreadPoolExecutor, as_completed

thread_local = threading.local()
max_workers = 8
base_url = "https://www.cvs.com"

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",    
    "connection": "Keep-Alive"
}

def sleep(min=3, max=3):
    duration = random.randint(min, max)
    time.sleep(duration)

def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name",
        "location_type","store_number", "street_address", "city", "state", "zip", "country_code","latitude", "longitude", "phone", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def get_session(reset=False):
    if not hasattr(thread_local, "session") or (reset == True):
        thread_local.session = SgRequests()
    return thread_local.session

def enqueue_links(url, selector):
    locs = []
    cities = []
    states = []

    get_session()
    r = session.get(url, headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.select(selector)

    for link in links:
        lurl = f"{base_url}{link['href']}"
        path_count = lurl.count("/")
        if path_count == 5:
            states.append(lurl)
        elif path_count == 6:
            if "cvs-pharmacy-address" in  lurl:
                locs.append(lurl)
            else:
                cities.append(lurl)
        else:
            raise Exception(f"invalid link: {lurl}") 

    return {
        "locs": locs,
        "cities": cities,
        "states": states
    }

def scrape_state_urls(state_urls, city_urls):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(enqueue_links, url, ".states a") for url in state_urls]
        for result in as_completed(futures):
            urls = result.result()
            city_urls.extend(urls["cities"])

def scrape_city_urls(city_urls, loc_urls):
    # scrape each city url and populate loc_urls with the results
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(enqueue_links, url, ".directions-link a") for url in city_urls]
        for result in as_completed(futures):
            d = result.result()
            loc_urls.extend(d["locs"])

def get_location(loc):
    print(f"Pulling Location: {loc}")

    session = get_session()
    r = session.get(loc, headers=headers)
    location = BeautifulSoup(r.text, "html.parser")
    script = location.select_one("#structured-data-block")
    if not script:
        print(f"Unable to fetch location: {loc}")
        return None

    structured_data = script.string

    info = json.loads(structured_data)[0]

    locator_domain = "cvs.com"
    page_url = loc
    location_name = info["name"]
    location_type = info["@type"]
    store_number = info["url"].split("/")[-1]
    street_address = info["address"]["streetAddress"]
    city = info["address"]["addressLocality"]
    state = info["address"]["addressRegion"]
    zipcode = info["address"]["postalCode"]
    country_code = info["address"]["addressCountry"]
    latitude = info["geo"]["latitude"]
    longitude = info["geo"]["longitude"]
    phone = info["address"]["telephone"]
    hours_of_operation = info["openingHours"]
    
    return [locator_domain, page_url, location_name, location_type, store_number, street_address, city, state, zipcode, country_code, latitude, longitude, phone, hours_of_operation]
    

def scrape_loc_urls(loc_urls):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(get_location, loc) for loc in loc_urls]
        for result in as_completed(futures):
            record = result.result()
            if record is not None:
                yield record

                
def fetch_data():
    urls = enqueue_links(f"{base_url}/store-locator/cvs-pharmacy-locations", ".states a")

    state_urls = urls["states"]
    city_urls = urls["cities"]
    loc_urls = urls["locs"]

    print(f"number of states: {len(state_urls)}")
    scrape_state_urls(state_urls, city_urls)

    print(f"number of cities: {len(city_urls)}")
    scrape_city_urls(city_urls, loc_urls)

    print(f"number of locations: {len(loc_urls)}")
    return scrape_loc_urls(loc_urls)
        

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
