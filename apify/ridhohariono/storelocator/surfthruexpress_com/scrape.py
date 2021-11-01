from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_usa
import re

DOMAIN = "surfthruexpress.com"
LOCATION_URL = "https://www.surfthruexpress.com/locations/"
API_URL = "https://www.surfthruexpress.com/wp-admin/admin-ajax.php?action=store_search&lat=36.81097&lng=-119.71365&max_results=100&search_radius=500&autoload=1"
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


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
    req = session.get(url, headers=HEADERS)
    if req.status_code == 404:
        return False
    soup = bs(req.content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    data = session.get(API_URL, headers=HEADERS).json()
    soup = pull_content(LOCATION_URL)
    hoo = (
        soup.find("div", {"id": "main-content"})
        .find(
            "div",
            {
                "class": "et_pb_module et_pb_text et_pb_text_1 et_pb_text_align_left et_pb_bg_layout_light"
            },
        )
        .find("div", {"class": "et_pb_text_inner"})
        .find_all("strong")
    )
    hoo_winter = (
        hoo[0]
        .get_text(strip=True, separator="@")
        .replace("Fall/Winter Hours@", "")
        .split("@")
    )
    hoo_spring = (
        hoo[1]
        .get_text(strip=True, separator="@")
        .replace("Spring/Summer Hours@", "")
        .split("@")
    )
    winter_hoo1 = re.split(r"(?: - )", hoo_winter[0])
    winter_hoo2 = re.split(r"(?: - )", hoo_winter[1])
    winter_name = (
        winter_hoo2[0].replace(", ", ",").replace(" & ", ",").strip().split(",")
    )
    for row in data:
        page_url = row["pricing_url"]
        location_name = row["store"].replace("&#038;", "&")
        street_address = row["address"] + " " + row["address2"]
        city = row["city"]
        state = row["state"]
        zip_postal = row["zip"]
        store_number = row["id"]
        phone = row["phone"]
        if not phone or len(phone) == 0:
            try:
                info = pull_content(page_url)
                phone = info.find("a", {"href": re.compile(r"tel:.*")}).text.strip()
            except:
                phone = MISSING
        country_code = "US" if row["country"] == "United States" else row["country"]
        location_type = MISSING
        latitude = row["lat"]
        longitude = row["lng"]
        hours_of_operation = ""
        if state in winter_name or city in winter_name:
            hours_of_operation = "Fall/Winter: " + " - ".join(winter_hoo2[1:])
        else:
            hours_of_operation = "Fall/Winter: " + winter_hoo1[1]
        hours_of_operation = hours_of_operation + ", Spring/Summer: " + hoo_spring[0]
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
