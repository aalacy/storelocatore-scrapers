import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_usa


DOMAIN = "spacealiens.com"
BASE_URL = "https://www.spacealiens.com"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


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


def pull_content(url, num=0):
    num += 1
    session = SgRequests()
    log.info("Pull content => " + url)
    try:
        soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    except Exception as e:
        if num < 3:
            return pull_content(url, num)
        raise e
    return soup


def get_info(data):
    info = {"addr": "", "phone": "", "hours": ""}
    for val in data:
        if (
            "Phone" not in val
            and "Fax" not in val
            and "day" not in val
            and "Hours" not in val
            and "Dining Room" not in val
            and "pm" not in val
        ):
            info["addr"] += val + " "
        elif "Phone" in val:
            info["phone"] = val.replace("Phone", "")
        elif "Hours" in val or "day" in val or "Dining Room" in val or "pm" in val:
            info["hours"] += val + " "
    return info


def get_latlong(url):
    longlat = re.search(r"!2d(-[\d]*\.[\d]*)\!3d(-?[\d]*\.[\d]*)", url)
    if not longlat:
        return MISSING, MISSING
    return longlat.group(2), longlat.group(1)


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(BASE_URL)
    contents = soup.find("a", text="Locations").find_next("ul").find_all("a")
    for row in contents:
        page_url = row["href"]
        store = pull_content(page_url)
        location_name = row.text.strip()
        info = get_info(
            re.sub(
                r"Contact Info@@",
                "",
                store.find_all("div", {"class": "motopress-text-obj"})[1].get_text(
                    strip=True, separator="@@"
                ),
            ).split("@@")
        )
        raw_address = info["addr"].strip()
        street_address, city, state, zip_postal = getAddress(raw_address)
        country_code = "US"
        phone = info["phone"].replace(":", "").strip()
        store_number = MISSING
        location_type = MISSING
        hours_of_operation = (
            info["hours"]
            .replace("Restaurant Hours", "")
            .replace(" Dining Room", ": Dining Room")
            .replace(" - CLOSED", ": CLOSED")
            .strip()
        )
        map_link = store.find("iframe")["src"]
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
