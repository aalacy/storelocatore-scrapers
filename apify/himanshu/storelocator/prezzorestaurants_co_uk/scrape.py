from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "prezzorestaurants.co.uk"
BASE_URL = "https://www.prezzorestaurants.co.uk"
STORES_URL = "https://www.prezzorestaurants.co.uk/find-and-book/search/?lat=51.502132&lng=-0.1887645&dist=2000&s=&p={}&f=&X-Requested-With=XMLHttpRequest"
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
                street_address = f"{street_address} {data.street_address_2}"
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
    try:
        soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    except:
        # Redirect and get current url
        if "?X-Requested-With=XMLHttpRequest":
            req = session.get(
                url.replace("?X-Requested-With=XMLHttpRequest", ""), headers=HEADERS
            )
            redirect_url = req.url
            soup = bs(
                session.get(
                    str(redirect_url) + "?X-Requested-With=XMLHttpRequest",
                    headers=HEADERS,
                ),
                "lxml",
            )
    return soup


def get_hoo(soup):
    try:
        hoo = re.sub(
            r",Christmas.*",
            "",
            soup.find("h4", text=re.compile(r"Opening times.*"))
            .find_next("div", {"class": "has-max-32-center has-text-left"})
            .get_text(strip=True, separator=",")
            .replace(":,", ": ")
            .strip(),
        )
    except:
        hoo = MISSING
    return hoo


def get_latlong(url):
    latlong = re.search(r"@(-?[\d]*\.[\d]*),(-?[\d]*\.[\d]*)", url)
    if not latlong:
        try:
            latlong = url.split("?ll=")[1].split("&z")[0].split(",")
            return latlong
        except:
            return MISSING, MISSING
    return latlong.group(1), latlong.group(2)


def fetch_data():
    log.info("Fetching store_locator data")
    num = 1
    while True:
        soup = pull_content(STORES_URL.format(num))
        contents = soup.find_all(
            "div", {"class": "column is-4 is-12-touch has-max-32-touch-center"}
        )
        if not contents:
            break
        for row in contents:
            is_closed = row.find("div", {"data-autoheight": "description"}).text.strip()
            if "Permanently closed" in is_closed:
                continue
            page_url = (
                BASE_URL
                + row.find("a", {"class": "button secondary-button w-100 px-i"})["href"]
            )
            store = pull_content(page_url + "?X-Requested-With=XMLHttpRequest")
            location_name = row.find("h4", {"data-autoheight": "header"}).text.strip()
            raw_address = str(
                " ".join(
                    row.find("div", {"data-autoheight": "address"})
                    .get_text(strip=True, separator=",")
                    .split()
                )
                .strip()
                .rstrip(",")
                .replace(", ,", ",")
            )
            street_address, city, state, zip_postal = getAddress(raw_address)
            if "None" in street_address or len(street_address) <= 3:
                street_address = raw_address.split(",")[0].strip()
            if city == MISSING:
                city = raw_address.split(",")[-2].strip()
            if "York" in city and city != "York":
                city = "York"
            if zip_postal == MISSING:
                zip = raw_address.split(",")[-1].strip()
                if len(zip) > 5 and len(zip) <= 8 and len(zip.split(" ")) > 1:
                    zip_postal = zip
            country_code = "UK"
            phone = row.find("a", {"href": re.compile(r"tel:.*")}).text.strip()
            hours_of_operation = get_hoo(store)
            location_type = MISSING
            store_number = MISSING
            map_link = row.find("a", text="View on google maps")["href"]
            latitude, longitude = get_latlong(map_link)
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
        num += 1


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
