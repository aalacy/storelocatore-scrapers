import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from sglogging import SgLogSetup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

logger = SgLogSetup().get_logger("minuteclinic_com")

allurls = []

thread_local = threading.local()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def write_output(data):
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for row in data:
            writer.write_row(row)


def random_sleep():
    time.sleep(random.random() * 2)


def get_session():
    if not hasattr(thread_local, "session"):
        thread_local.session = SgRequests()
    return thread_local.session


def get_state_urls():
    state_urls = []
    session = get_session()
    url = "https://www.cvs.com/minuteclinic/clinic-locator/"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if 'title="Locations in' in line:
            lurl = line.split('href="')[1].split('"')[0]
            state_urls.append(lurl)
    return state_urls


def get_city_urls(state_urls):
    cities_all = []

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(get_cities_in_state, url) for url in state_urls]
        for result in as_completed(futures):
            cities_all.extend(result.result())

    return cities_all


def get_cities_in_state(state_url):
    cities = []
    session = get_session()
    random_sleep()
    r = session.get(state_url, headers=headers)
    logger.info(state_url)
    for line in r.iter_lines():
        if 'title="Locations in' in line:
            lurl = line.split('href="')[1].split('"')[0]
            cities.append(lurl)

    return cities


def get_location_urls(city_urls):
    locations_all = []

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(get_locations_in_city, url) for url in city_urls]
        for result in as_completed(futures):
            locations_all.extend(result.result())

    return locations_all


def get_locations_in_city(city_url):
    locs = []
    session = get_session()
    logger.info(city_url)
    random_sleep()
    r = session.get(city_url, headers=headers)

    for line in r.iter_lines():
        if 'class="covid-standalone-details">' in line:
            locs.append(line.split('href="')[1].split('"')[0])

    return locs


def fetch_data():

    state_urls = get_state_urls()
    city_urls = get_city_urls(state_urls)
    loc_urls = get_location_urls(city_urls)

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(get_location, url) for url in loc_urls]
        for result in as_completed(futures):
            record = result.result()
            if record is not None:
                yield record


def get_location(url):

    try:
        session = get_session()
        logger.info(url)
        website = "minuteclinic.com"
        typ = "<MISSING>"
        hours = ""
        name = "Minute Clinic"
        add = ""
        city = ""
        country = "US"
        state = ""
        zc = ""
        phone = ""
        lat = ""
        lng = ""
        store = url.rsplit("/", 1)[1].split(".")[0]

        random_sleep()
        response = session.get(url, headers=headers)

        if response.url != url and "cvs-pharmacy-address" in response.url:
            return None

        for line2 in response.iter_lines():
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if '"openingHours": "' in line2:
                hours = line2.split('"openingHours": "')[1].split('"')[0].strip()
            if '"latitude": "' in line2:
                lat = line2.split('"latitude": "')[1].split('"')[0]
            if '"longitude": "' in line2:
                lng = line2.split('"longitude": "')[1].split('"')[0]

        if hours == "":
            hours = "<MISSING>"

        if url not in allurls:
            allurls.append(url)
            if "133 Peachtree St" in add:
                phone = "(404) 522-6330"
            if "sanantonio/7829" in url:
                add = "16580 Huebner Road"
                city = "San Antonio"
                state = "TX"
                zc = "78248"
                lat = "<MISSING>"
                lng = "<MISSING>"
                phone = "<MISSING>"
                hours = "<MISSING>"
            return SgRecord(
                locator_domain=website,
                page_url=url,
                location_name=name,
                street_address=add,
                city=city,
                state=state,
                zip_postal=zc,
                country_code=country,
                store_number=store,
                phone=phone,
                location_type=typ,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours,
            )
    except:
        pass


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
