from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "d1sportstraining.com"
BASE_URL = "https://www.d1training.com"
API_URL = "https://www.d1training.com/locations/?CallAjax=GetLocations"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    req = session.get(url, headers=HEADERS)
    if req.status_code == 404:
        return False
    soup = bs(req.content, "lxml")
    return soup


def get_hoo(url, id):
    log.info(f"Get hours of operation for => {url}")
    try:
        payload = {
            "_m_": "HoursPopup",
            "HoursPopup$_edit_": id,
            "HoursPopup$_command_": "",
        }
        soup = bs(
            session.post(url + "?L=true", headers=HEADERS, data=payload).content, "lxml"
        )
        hoo = (
            soup.find("table", {"class": "ui-repeater"})
            .get_text(strip=True, separator=",")
            .replace("day,", "day: ")
        )
    except:
        return MISSING
    return hoo.strip()


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(API_URL, headers=HEADERS).json()
    for row in data:
        page_url = BASE_URL + row["Path"]
        location_name = row["FranchiseLocationName"]
        street_address = (row["Address1"] + " " + row["Address2"]).strip()
        city = row["City"]
        state = row["State"]
        zip_postal = row["ZipCode"]
        phone = row["Phone"]
        country_code = "US" if row["Country"] == "USA" else row["Country"]
        store_number = row["FranchiseLocationID"]
        hours_of_operation = get_hoo(page_url, store_number)
        latitude = row["Latitude"]
        longitude = row["Longitude"]
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
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
