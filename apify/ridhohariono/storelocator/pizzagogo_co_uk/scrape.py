import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "pizzagogo.co.uk"
BASE_URL = "https://www.pizzagogo.co.uk/"
LOCATION_URL = "https://www.pizzagogo.co.uk/ajax/?do=all_stores_for_map"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
MISSING = "<MISSING>"

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_hours(page_url):
    soup = pull_content(page_url)
    try:
        hoo = soup.find("table", {"class": "padded_table"}).get_text(
            strip=True, separator=" "
        )
    except:
        hoo = (
            soup.find("div", {"class": "single_store_times"})
            .find("table")
            .get_text(strip=True, separator=" ")
        )
    return hoo.strip()


def split_info(val):
    return val.split("|")


def fetch_data():
    store_json = session.get(LOCATION_URL, headers=HEADERS).json()
    store_info = {
        "store_ids": split_info(store_json["store_ids"]),
        "stores": split_info(store_json["stores"]),
        "address": split_info(store_json["address_arr"]),
        "phone": split_info(store_json["phone_arr"]),
        "lat": split_info(store_json["lat_arr"]),
        "lng": split_info(store_json["lng_arr"]),
    }
    for i in range(len(store_info["store_ids"])):
        store_number = store_info["store_ids"][i]
        page_url = BASE_URL + "gotostore/{}".format(store_number)
        location_name = store_info["stores"][i]
        parse_addr = (
            store_info["address"][i]
            .replace("\r", ",")
            .replace("<br />", ",")
            .strip()
            .replace(",,", ",")
        )
        address = re.sub(r",\s+,", ",", parse_addr).strip().split(",")
        if len(address) > 4:
            street_address = ", ".join(address[:2])
        else:
            street_address = address[0].strip()
        if len(address) > 2:
            if len(address) > 4:
                city = address[2].strip()
            else:
                city = address[1].strip()
        else:
            city = location_name
        city = re.sub(r"\(.*\)", "", city).strip()
        state = MISSING
        zip_postal = address[-1].strip()
        phone = store_info["phone"][i]
        country_code = "GB"
        latitude = store_info["lat"][i]
        longitude = store_info["lng"][i]
        hours_of_operation = get_hours(page_url)
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
