from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import re
import json

DOMAIN = "crazyshirts.com"
BASE_URL = "https://www.crazyshirts.com"
LOCATION_URL = "https://www.crazyshirts.com/store-locator/all-stores.do"
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
    longlat = re.search(r"!2d(-[\d]*\.[\d]*)\!3d(-?[\d]*\.[\d]*)", url)
    if not longlat:
        return "<MISSING>", "<MISSING>"
    return longlat.group(2), longlat.group(1)


def get_json(soup):
    script = soup.find(
        "script",
        string=re.compile(r"MarketLive.StoreLocator.storeLocatorDetailPageReady"),
    )
    data = re.search(
        r'{"resultCount":1,"results":\[(.*)\]}', script.string, re.MULTILINE
    )
    return json.loads(data.group(1))


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.find_all("div", {"class": "eslStore ml-storelocator-headertext"})
    for row in contents:
        page_url = BASE_URL + row.find("a")["href"]
        location_name = row.text.strip()
        if "STORE CLOSED" in location_name:
            continue
        content = pull_content(page_url)
        info = get_json(content)
        street_address = info["address"]["street1"]
        if info["address"]["street2"]:
            street_address += ", " + info["address"]["street2"]
        if info["address"]["street3"]:
            street_address += ", " + info["address"]["street3"]
        city = info["address"]["city"]
        state = info["address"]["stateCode"]
        zip_postal = info["address"]["postalCode"]
        phone = info["address"]["phone"]
        content.find("span", {"class": "ml-storelocator-hours-details"}).find(
            "strong"
        ).decompose()
        content.find("span", {"class": "ml-storelocator-hours-details"}).find(
            "a"
        ).decompose()
        hours_of_operation = content.find(
            "span", {"class": "ml-storelocator-hours-details"}
        ).get_text(strip=True, separator=",")
        country_code = "us"
        store_number = MISSING
        location_type = "crazyshirts"
        latitude = info["location"]["latitude"]
        longitude = info["location"]["longitude"]
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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
