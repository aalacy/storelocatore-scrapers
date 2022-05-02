from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "creamscafe.com"
LOCATION_URL = "https://www.creamscafe.com/our-stores/"
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


def get_latlong(url):
    longlat = re.search(r"!2d(-?[\d]*\.[\d]*)\!3d(-?[\d]*\.[\d]*)", url)
    if not longlat:
        return MISSING, MISSING
    return longlat.group(2), longlat.group(1)


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.select("div.the_content_wrapper a")
    for row in contents:
        try:
            page_url = row["href"]
        except:
            continue
        next_element = row.find_next()
        if next_element.name == "strong" and "Coming Soon" in next_element.text.strip():
            continue
        store = pull_content(page_url)
        info = store.find("strong", text="Address:").parent.parent
        location_name = row.text.strip()
        raw_address = (
            info.find("strong", text="Address:")
            .parent.get_text(strip=True, separator=",")
            .replace("Address:,", "")
            .replace(" ", " ")
            .strip()
        )
        street_address, city, state, zip_postal = getAddress(raw_address)
        if city == MISSING:
            city = location_name
        phone = (
            (
                info.find("strong", text="Telephone:")
                .parent.text.replace("Telephone:", "")
                .strip()
            )
            .replace("TBA", "")
            .replace("TBC", "")
            .strip()
        )
        hoo_content = info.find_all("p", {"class": "xmsonormal"})
        if hoo_content:
            hoo = ""
            for hours in hoo_content:
                hoo += hours.text.strip() + ","
        else:
            try:
                hoo = re.sub(
                    r"Opening Times.*:,|Dine-in:,?|/?\s?Dine-in|Hot Section.*|\(.*\)",
                    "",
                    info.find(
                        "strong", text=re.compile(r"Opening Times.*")
                    ).parent.get_text(strip=True, separator=","),
                )
            except:
                hoo = ""
        hours_of_operation = (
            re.sub(
                r"Opening Times.*:,|Dine-in:,?|/?\s?Dine-in|Hot Section.*|\(.*\)",
                "",
                hoo,
            )
            .rstrip(",")
            .replace(" ", "")
            .strip()
        )
        location_type = MISSING
        ext_name = row.find_next().text.strip()
        if "Opening Soon" in ext_name or "Coming Soon" in ext_name:
            location_type = "Coming Soon"
            location_name = location_name + " - Coming Soon"
        elif "Temp Closed" in ext_name:
            location_type = "Temp Closed"
            location_name = location_name + " - Temp Closed"
        if hours_of_operation == "Opening Times:":
            hours_of_operation = (
                info.find("strong", text=re.compile(r"Opening Times.*"))
                .parent.find_next("p")
                .get_text(strip=True, separator=",")
                .replace(" ", "")
                .strip()
            )
        elif "Temporarily closed" in hours_of_operation:
            location_type = "TEMP_CLOSED"
        country_code = "GB"
        store_number = MISSING
        map_link = store.find("iframe", {"src": re.compile(r"\/maps\/embed\?.*")})[
            "src"
        ]
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
