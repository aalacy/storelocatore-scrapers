from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
import re

DOMAIN = "igakorea.com"
LOCATION_URL = "http://igakorea.com/sub_05d.aspx?page={page}&sido=&gugun=&store=&act=info.page&pcode=sub5_4"
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


def get_available_stores(url, try_num=1):
    soup = pull_content(url)
    try:
        soup.find("table", {"id": "htblList"}).find_all("tr")[1].find(
            "a", {"class": "news"}
        ).text
    except:
        if try_num <= 3:
            log.info(f"Store element are not available. Retry ({try_num}) times")
            try_num += 1
            return get_available_stores(url, try_num)
        else:
            return False
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    num = 1
    while True:
        page_url = LOCATION_URL.format(page=num)
        soup = get_available_stores(page_url)
        if not soup:
            break
        contents = soup.find("table", {"id": "htblList"}).find_all("tr")
        phone = (
            soup.find("div", {"class": "footer-area"})
            .find("p", {"class": "footer-info"})
            .find("a", {"href": re.compile(r"tel:.*")})["href"]
            .replace("tel:", "")
        )
        for row in contents[1:]:
            location_name = row.find("a", {"class": "news"}).text.strip()
            raw_address = row.select_one("td:nth-child(3)").text.strip()
            street_address, city, state, zip_postal = getAddress(raw_address)
            country_code = "KR"
            store_number = re.sub(r"\D+", "", row.find("td").text).strip()
            hours_of_operation = MISSING
            location_type = MISSING
            latitude = MISSING
            longitude = MISSING
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
