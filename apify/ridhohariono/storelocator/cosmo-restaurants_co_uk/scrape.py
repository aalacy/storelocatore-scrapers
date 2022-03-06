from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import re


DOMAIN = "cosmo-restaurants.co.uk"
BASE_URL = "https://www.cosmo-restaurants.co.uk"
LOCATION_URL = "https://www.cosmo-restaurants.co.uk/restaurants"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode
            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"No valid address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_hoo(hours_contents):
    hoo = ""
    for row in hours_contents:
        hoo += row["type"] + ": "
        for hday in row["content"]:
            day = hday.find(
                "span", {"class": "restaurant-times-prices__block__days"}
            ).text.strip()
            hour = hday.find(
                "span", {"class": "restaurant-times-prices__block__time"}
            ).text.strip()
            hoo += day + ": " + hour + ","
    return hoo.rstrip(",")


def get_latlong(url):
    latlong = re.search(r"@(-?[\d]*\.[\d]*),(-?[\d]*\.[\d]*)", url)
    if not latlong:
        return MISSING, MISSING
    return latlong.group(1), latlong.group(2)


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.find("main", id="main").find_all("div", {"class": "restaurant"})
    for row in contents:
        if "Coming Soon" in row.text.strip():
            continue
        page_url = row.find("a")["href"]
        location_name = row.find(
            "div", {"class": "restaurant__content__title"}
        ).text.strip()
        if "Temporarily Closed" in row.text.strip():
            raw_address = " ".join(
                row.find("div", {"class": "restaurant__content__address"})
                .text.strip()
                .replace("Leave feedback here", "")
                .split()
            ).strip()
            phone = MISSING
            hours_of_operation = MISSING
            location_type = "TEMP_CLOSED"
            latitude = MISSING
            longitude = MISSING
        else:
            store = pull_content(page_url)
            info = store.find("div", {"class": "restaurant-location"})
            raw_address = (
                info.find("p")
                .get_text(strip=True, separator=" ")
                .replace("Leave feedback here", "")
                .strip()
            )
            phone = row.find(
                "div", {"class": "restaurant__content__contact"}
            ).text.strip()
            hoo_lunch = store.find("div", id="tab-1").find_all(
                "div", {"class": "restaurant-times-prices__block"}
            )
            hoo_dinner = store.find("div", id="tab-2").find_all(
                "div", {"class": "restaurant-times-prices__block"}
            )
            hours_of_operation = get_hoo(
                [
                    {"type": "Lunch", "content": hoo_lunch},
                    {"type": "Dinner", "content": hoo_dinner},
                ]
            )
            if "Temporarily Closed" in hours_of_operation:
                location_type = "TEMP_CLOSED"
            else:
                location_type = MISSING
            try:
                map_link = info.find("a", {"href": re.compile(r"\/maps\/place")})[
                    "href"
                ]
                latitude, longitude = get_latlong(map_link)
            except:
                latitude = MISSING
                longitude = MISSING
        street_address, city, state, zip_postal = getAddress(raw_address)
        if city == MISSING:
            city = location_name
        if zip_postal == MISSING:
            zip_postal = raw_address.split(",")[-1].replace(city, "").strip()
            street_address = re.sub(
                city + r".*|" + zip_postal + r".*", "", street_address
            )
        store_number = MISSING
        country_code = "GB"
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
