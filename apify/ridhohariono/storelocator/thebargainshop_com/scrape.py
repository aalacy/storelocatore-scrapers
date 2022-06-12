from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import json
import re

DOMAIN = "thebargainshop.com"
BASE_URL = "https://www.thebargainshop.com"
STATE_INFO = "https://www.thebargainshop.com/ajax_store.cfm?action=provinces"
STORE_STATE = (
    "https://www.thebargainshop.com/ajax_store.cfm?province={state}&action=cities"
)
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
    if req.status_code == 404:
        return False
    soup = bs(req.content, "lxml")
    return soup


def get_name_and_type(label, roles):
    for x in roles:
        if x["meta"]:
            return (x["meta"]["title"] + " - " + label).strip(), x["meta"]["title"]


def fetch_data():
    log.info("Fetching store_locator data")
    states = session.get(STATE_INFO, headers=HEADERS).json()
    for state_info in states["data"]:
        stores = session.get(
            STORE_STATE.format(state=state_info["val"]), headers=HEADERS
        ).json()
        for row in stores["data"]:
            page_url = BASE_URL + row["val"]
            soup = pull_content(page_url)
            info = re.search(
                r"article = (.*)",
                soup.find(
                    "div",
                    {
                        "class": re.compile(
                            r"article_(.*) article_detail_full article_type_article"
                        )
                    },
                )
                .find("script")
                .string,
            )
            info = json.loads(info.group(1))
            location_name, location_type = get_name_and_type(
                row["label"], info["roles"]
            )
            street_address = info["locations"][0]["address"]
            city = info["locations"][0]["city"]
            state = info["locations"][0]["provstate"]
            zip_postal = info["locations"][0]["postalzip"].replace("-", " ")
            country_code = info["locations"][0]["country"]
            phone = info["locations"][0]["phone"]
            store_number = info["name"]
            latitude = info["locations"][0]["lat"]
            longitude = info["locations"][0]["lon"]
            hoo = json.loads(info["meta"]["google_structured_data"])[
                "openingHoursSpecification"
            ]
            hours_of_operation = ""
            for i in range(len(hoo)):
                day = hoo[i]["dayOfWeek"][0]
                if day in hours_of_operation:
                    continue
                hours = hoo[i]["opens"] + " - " + hoo[i]["closes"]
                hours_of_operation += day + ": " + hours + ","
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
                raw_address=f"{street_address}, {city}, {state} {zip_postal}",
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
