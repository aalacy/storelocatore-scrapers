import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl

DOMAIN = "spar.dk"
BASE_URL = "https://www.spar.dk"
API_URL = "https://spar.dk/search"
HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
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


def cleanhtml(raw_html):
    pattern = re.compile("<.*?>")
    cleantext = re.sub(pattern, "", raw_html)
    return cleantext


def fetch_data():
    log.info("Fetching store_locator data")
    payload = {
        "params": {"wt": "json"},
        "filter": [],
        "query": 'ss_search_api_datasource:"entity:node" AND bs_status:true AND ss_type:"store"',
        "limit": 1000,
    }
    data = session.post(API_URL, json=payload).json()
    for row in data["response"]["docs"]:
        page_url = BASE_URL + row["ss_path_alias"]
        location_name = row["tm_X3b_en_title"][0]
        street_address = cleanhtml(row["tm_X3b_en_address_line1"][0])
        city = cleanhtml(row["tm_X3b_en_locality"][0])
        state = MISSING
        zip_postal = cleanhtml(row["tm_X3b_en_postal_code"][0])
        phone = row["ss_field_store_phone"]
        country_code = "DK"
        store_number = MISSING
        location_type = row["ss_type"]
        latitude = row["fts_lat"]
        longitude = row["fts_lon"]
        if "itm_starthours" not in row or row["itm_starthours"] == 0:
            hours_of_operation = MISSING
        else:
            days = [
                "Mandag",
                "Tirsdag",
                "Onsdag",
                "Torsdag",
                "Fredag",
                "Lørdag",
                "Søndag",
            ]
            hoo = ""
            for i in range(len(days)):
                hoo += (
                    days[i]
                    + ": "
                    + str(row["itm_starthours"][i])
                    + " - "
                    + str(row["itm_endhours"][i])
                    + ","
                )
            hours_of_operation = re.sub(
                r"(\d{1,2})(\d{2})", r"\1:\g<2>", hoo.strip()
            ).rstrip(",")
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
