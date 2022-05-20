from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "meadowsfrozencustard.com"
BASE_URL = "https://meadowsfrozencustard.com"
LOCATION_URL = "https://meadowsfrozencustard.com/columns/"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()
MISSING = "<MISSING>"


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
    req = session.get(url, headers=HEADERS)
    soup = bs(req.content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.select("article div.entry-content div.col-lg-3.col-md-3.col-sm-3")
    for row in contents:
        page_url = row.find("h3").find("a")["href"]
        if DOMAIN not in page_url:
            page_url = BASE_URL + page_url
        store = pull_content(page_url)
        location_name = row.find("h3").text.strip()
        addr = row.select_one("p:nth-child(3)")
        if not addr:
            addr = row.select_one("p:nth-child(2)")
        raw_address = addr.get_text(strip=True, separator=",").replace("\n", "").strip()
        street_address, city, state, zip_postal = getAddress(raw_address)
        country_code = "US"
        if len(zip_postal) < 5:
            if "South Wales" in raw_address:
                country_code = "AU"
        phone = (
            store.find("strong", text="Contact Information")
            .parent.text.replace("Contact Information", "")
            .replace("Phone: ", "")
            .strip()
        )
        if "Address:" in phone:
            phone = MISSING
        if "Hours" in phone:
            hours_of_operation = phone.split("Hours")[1].replace(":", "").strip()
            phone = re.sub(r"Hours.*", "", phone).strip()
        else:
            hour1 = store.find("div", {"class": "about-location"})
            hour2 = list(hour1.stripped_strings)
            if "columbia-md" in page_url:
                hour = (
                    store.find("strong", text="Store Hours")
                    .find_next("p")
                    .get_text(strip=True, separator=",")
                    .replace(":,", ": ")
                    .strip()
                )
            else:
                try:
                    if len(hour2) < 2:
                        hour1 = store.find_all("div", {"class": "about-location"})[1]
                        hour2 = list(hour1.stripped_strings)
                    hour = ""
                    for line in hour2:
                        if (
                            "pm" in line.lower()
                            or ":00" in line.lower()
                            or ":30" in line.lower()
                            or ": closed" in line.lower()
                            or "OPEN DAILY" in line.upper()
                        ):
                            hour = (
                                hour
                                + " "
                                + line.replace("–", "-").replace("Hours:", "Daily:")
                            ).strip()
                    if "Open Daily" in hour:
                        hour = hour[
                            hour.find("Open Daily") : hour.rfind("pm") + 2
                        ].strip()
                    if "(" in hour:
                        hour = hour[: hour.find("(")].strip()
                    if "P.M" in hour:
                        hour = hour[: hour.rfind("P.M") + 3].strip()
                    if "PM" in hour:
                        hour = hour[: hour.rfind("PM") + 2].strip()
                    if "Fall" in hour:
                        hour = hour[: hour.find("Fall")].strip()
                    if not hour:
                        hour = MISSING
                except:
                    hour = MISSING
                if "Our custard is made fresh all day" in hour:
                    hour = re.sub(r"Our.*|We\’re", "", hour).strip()
        hours_of_operation = hour.replace("\n", "").strip()
        store_number = MISSING
        try:
            map_link = store.iframe["src"]
            lat_pos = map_link.rfind("!3d")
            latitude = map_link[lat_pos + 3 : map_link.find("!", lat_pos + 5)].strip()
            lng_pos = map_link.find("!2d")
            longitude = map_link[lng_pos + 3 : map_link.find("!", lng_pos + 5)].strip()
        except:
            latitude = MISSING
            longitude = MISSING
        location_type = MISSING
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
