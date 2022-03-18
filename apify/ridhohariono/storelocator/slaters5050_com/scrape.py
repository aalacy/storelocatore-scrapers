from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_usa
import re

DOMAIN = "slaters5050.com"
BASE_URL = "https://slaters5050.com/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

MISSING = "<MISSING>"


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_usa(raw_address)
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


def get_latlong(url):
    longlat = re.search(r"!2d(-[\d]*\.[\d]*)\!3d(-?[\d]*\.[\d]*)", url)
    if not longlat:
        return MISSING, MISSING
    return longlat.group(2), longlat.group(1)


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(BASE_URL)
    contents = (
        soup.find("footer")
        .find("nav", {"class": "locations-nav"})
        .find_all("a", {"href": re.compile(r"\/locations\/.*")})
    )
    for row in contents:
        page_url = row["href"]
        info = pull_content(page_url)
        if "las-vegas" in page_url:
            addr = (
                info.select_one(
                    "div.vc_column-inner.vc_custom_1512389166631 div.wpb_text_column.wpb_content_element"
                )
                .get_text(strip=True, separator="@@")
                .split("@@")
            )
            location_name = addr[0]
            raw_address = ",".join(addr[1:-2])
            phone = addr[-2]
            hours_of_operation = (
                info.find(
                    "div",
                    {
                        "class": "wpb_text_column wpb_content_element vc_custom_1585601459333"
                    },
                )
                .find("p")
                .text.strip()
                .replace("HOURS", "")
            )
            map_link = info.find("iframe")["src"]
            latitude, longitude = get_latlong(map_link)
            location_type = MISSING
        else:
            location_name = row.text
            hoo_content = info.find("div", {"class": "hours"}).find("p")
            if "Coming Soon" in hoo_content.text.strip():
                location_type = "COMING_SOON"
                phone = MISSING
            else:
                phone = info.find("p", {"class": "phone"}).text.strip()
                location_type = MISSING
            raw_address = info.find("p", {"class": "address"}).get_text(
                strip=True, separator=","
            )
            hours_of_operation = hoo_content.get_text(strip=True, separator=",")
            latitude = MISSING
            longitude = MISSING
        street_address, city, state, zip_postal = getAddress(raw_address)
        country_code = "US"
        store_number = MISSING
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
