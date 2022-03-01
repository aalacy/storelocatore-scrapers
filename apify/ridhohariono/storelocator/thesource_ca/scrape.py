from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json


DOMAIN = "thesource.ca"
BASE_URL = "https://www.thesource.ca"
LOCATION_URL = "https://www.thesource.ca/en-ca/store-finder?latitude=43.0&longitude=-79.0&q=&popupMode=false&page={}&show=All"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


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


def fetch_data():
    log.info("Fetching store_locator data")
    page = 0
    while True:
        stores_url = LOCATION_URL.format(page)
        soup = pull_content(stores_url)
        contents = soup.select("table.store-results-list.desktop-only tr.storeItem")
        if not contents:
            break
        num = 0
        location_list = json.loads(soup.find("div", id="map_canvas")["data-stores"])
        for row in contents:
            info = row.find("div", {"class": "details"})
            location_name = info.find("div", {"class": "itemName"}).text.strip()
            raw_address = (
                info.find("ul")
                .get_text(strip=True, separator="@@")
                .replace("HAPPY VALLEY,", "")
                .strip()
            )
            addr = raw_address.split("@@")
            if len(addr) == 4:
                street_address = " ".join((addr[0] + "," + addr[1]).split())
                city_state = addr[2].split(",")
                city = city_state[0].replace("(CHARNY)", "").strip()
                state = city_state[1].strip()
                zip_postal = addr[3].strip()
            else:
                street_address = addr[0].strip()
                city_state = addr[1].split(",")
                city = city_state[0].strip()
                state = city_state[1].strip()
                zip_postal = addr[2].strip()
            country_code = "CA"
            phone = info.find("a", {"class": "tel-link"}).text.strip()
            location_type = MISSING
            store_number = row.find("a", {"class": "make-my-store"})["data-store"]
            hours_of_operation = (
                row.find("td", {"class": "hours"})
                .get_text(strip=True, separator=",")
                .replace("Sun,", "Sunday: ")
                .replace("Sat,", "Saturday: ")
                .replace("Fri,", "Friday: ")
                .replace("Mon,", "Monday: ")
                .replace("Tue,", "Tuesday: ")
                .replace("Wed,", "Wednesday: ")
                .replace("Thu,", "Thurseday: ")
            )
            latlong = location_list["store" + str(num)]
            if latlong["latitude"] == "0.0":
                latitude = MISSING
                longitude = MISSING
            else:
                latitude = latlong["latitude"]
                longitude = latlong["longitude"]
            page_url = BASE_URL + "/store/" + store_number
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
        page += 1


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
