from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "gnc.com.ph"
LOCATION_URL = "https://www.gnc.com.ph/en/stores"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
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
    HEADERS["Referer"] = url
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_latlong(url):
    latlong = re.search(r"@(-?[\d]*\.[\d]*),(-?[\d]*\.[\d]*)", url)
    if not latlong:
        return "<MISSING>", "<MISSING>"
    return latlong.group(1), latlong.group(2)


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.find("div", {"class": "row store-locator__list mt-2"}).find_all(
        "div", {"class": "col-sm-6 col-md-4 mb-4 pb-2 store-locator__list__item"}
    )
    for row in contents:
        info = (
            row.find("div").find("div").get_text(strip=True, separator="@@").split("@@")
        )
        location_name = info[0]
        raw_address = " ".join(info[1:]).replace("\n", ",").strip().rstrip(",")
        street_address, city, state, _ = getAddress(raw_address)
        try:
            phone = row.find("div", {"class": "mt-3"}).find("a").text.strip()
            row.find("div", {"class": "mt-3"}).find(
                "p", {"class": "text--dark"}
            ).decompose()
        except:
            phone = MISSING
        zip_postal = MISSING
        if "pasig" in raw_address.lower():
            city = "Pasig"
        elif "muntinlupa" in raw_address.lower():
            city = "Muntinlupa"
        elif "baguio" in raw_address.lower():
            city = "Baguio"
        elif "quezon" in raw_address.lower():
            city = "Quezon City"
        elif "parañaque" in raw_address.lower():
            city = "Parañaque City"
        elif "makati " in raw_address.lower():
            city = "MAKATI"
        elif "mandurriao Iloilo City" in raw_address.lower():
            city = "Mandurriao Iloilo City"
        elif "calamba" in raw_address.lower():
            city = "Calamba"
        elif "jaro iloilo" in raw_address.lower():
            city = "Jaro Iloilo"
        elif "sta. rosa" in raw_address.lower():
            city = "Sta. Rosa"
        elif "san juan" in raw_address.lower():
            city = "SAN JUAN"

        if "north" in raw_address.lower():
            state = "North"
        elif "south" in raw_address.lower():
            state = "SOUTH"
        elif "manila" in raw_address.lower():
            state = "Manila"
        if "north luzon" in raw_address.lower():
            state = "North Luzon"
        country_code = "PH"
        store_number = MISSING
        hours_of_operation = (
            row.find("div", {"class": "mt-3"})
            .get_text(strip=True, separator=",")
            .replace("Store Hours: ", "")
        )
        try:
            map_link = row.find("a", {"class": "store-locator__list__item__icon"})[
                "href"
            ]
            latitude, longitude = get_latlong(map_link)
        except:
            latitude = MISSING
            longitude = MISSING
        location_type = MISSING
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=LOCATION_URL,
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
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
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
