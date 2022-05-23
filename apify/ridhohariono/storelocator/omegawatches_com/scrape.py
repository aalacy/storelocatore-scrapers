import json
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import re


DOMAIN = "omegawatches.com"
BASE_URL = "https://www.omegawatches.com/"
LOCATION_URL = "https://www.omegawatches.com/store"
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
    req = session.get(url, headers=HEADERS)
    if req.status_code == 200:
        soup = bs(req.content, "lxml")
    else:
        return False
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    data = json.loads(
        soup.find("script", text=re.compile("var stores ="))
        .text.split("var stores = ")[1]
        .split("; var pm_countries")[0]
    )
    for row in data:
        page_url = (BASE_URL + row["websiteUrl"]) or LOCATION_URL
        store = pull_content(page_url)
        location_name = row["name"].replace("<br />", " ").strip()
        if not location_name:
            location_name = row["cityName"]
        raw_address = row["adrOnly"].replace("<br />", ",").strip().rstrip(",")
        if not raw_address:
            raw_address = row["cityName"]
        street_address, city, state, zip_postal = getAddress(raw_address)
        if street_address == MISSING:
            street_address = row["adrOnly"].replace("<br />", ",").strip()
        if state == MISSING:
            state = row["stateName"] or MISSING
        if city == MISSING:
            city = row["cityName"] or MISSING
        if zip_postal == MISSING:
            zip_postal = row["zipcode"] or MISSING
        if state == "Los Angeles" or state == "San Francisco":
            city = state
            state = "CA"
        elif state == "Honolulu":
            city = "Honolulu"
            state = MISSING
        country_code = row["countryCode"]
        location_type = "BOUTIQUE" if row["is_boutique"] == 1 else "RETAILERS"
        try:
            phone = (
                store.find("a", {"class": "ow-store-view__tel"})
                .text.replace("T.", "")
                .strip()
            )
        except:
            phone = MISSING
        if phone == MISSING:
            phone = row["contacts"]["phone"]
            if not phone:
                phone = row["contacts"]["fax"] or MISSING
        try:
            hours_of_operation = store.find(
                "ul", {"class": "ow-store-view__opening"}
            ).get_text(strip=True, separator=" ")
        except:
            hours_of_operation = MISSING
        is_closed = (
            " ".join(
                re.sub(
                    r"Dostęp do.*|www.*|Ouverture.*|Actuellement Fermé.*|(Opening|Opeing)? hours may vary due to Covid.*|,?\s?Public Holiday|Sujeto a modificaciones debido a disposiciones sanitarias por COVID 19|Daily opening hour according to flight schedule|Open for every outbound International flight|Closed Good Friday and Christmas Day|follow the opening hour of department store|Please note our current opening hours:, , |Free and private.*|Last appointment.*|Servicing Center opening hours,|Recomendamos.*|Open depending on flight.*",
                    "",
                    row["remarks"].replace("<br />", ", ").replace("〜", "-"),
                ).split()
            )
            .strip()
            .rstrip(",")
            or MISSING
        )
        if (
            "emporarily closed" in is_closed
            or "Ouverture" in is_closed
            or "under renovation" in is_closed
            or "temporary" in is_closed
        ):
            location_name = location_name + " - Temporarily closed"
        store_number = row["id"]
        latitude = MISSING if row["latitude"] == 0 else row["latitude"]
        longitude = MISSING if row["longitude"] == 0 else row["longitude"]
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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.ZIP})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
