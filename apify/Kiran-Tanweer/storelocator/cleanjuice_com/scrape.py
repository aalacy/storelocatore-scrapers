import re
from bs4 import BeautifulSoup
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


session = SgRequests()
website = "cleanjuice_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "www.cleanjuice_com"
MISSING = SgRecord.MISSING

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def is_coming_soon(url):
    soup = BeautifulSoup(session.get(url, headers=headers).content, "lxml")
    coming_soon = soup.select_one(
        "div#content-area  div.container  div.subcontent  div.subright"
    )
    if coming_soon and re.search(
        r"COMING SOON", coming_soon.text.strip(), flags=re.IGNORECASE
    ):
        return True
    return False


def fetch_data():
    search_url = "https://www.cleanjuice.com/wp-admin/admin-ajax.php?action=store_search&lat=35.227087&lng=-80.843127&max_results=50&search_radius=50&autoload=1"
    stores_req = session.get(search_url, headers=headers).json()
    for store in stores_req:
        link = store["permalink"]
        if is_coming_soon(link):
            continue
        street1 = store["address"]
        title = store["store"].replace(" ", " ").strip()
        storeid = store["id"]
        street2 = store["address2"]
        city = store["city"]
        state = store["state"]
        pcode = store["zip"]
        country = store["country"]
        lat = store["lat"]
        lng = store["lng"]
        phone = store["phone"]
        if not store["hours"]:
            hours = MISSING
        else:
            hours = BeautifulSoup(store["hours"], "lxml")
            hours = hours.text
            hours = hours.replace("day", "day ")
            hours = hours.replace("PM", "PM ")
            hours = hours.rstrip("Order Now")
        street = (street1 + " " + street2).replace(" ", " ").strip()
        if country == "United States":
            country = "US"
        pcode = pcode.replace("]", "").strip()
        if hours == MISSING:
            location_type = "TEMP_CLOSED"
        else:
            location_type = MISSING
        log.info("Append {} => {}".format(title, street))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=link,
            location_name=title,
            street_address=street,
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode,
            country_code=country,
            store_number=storeid,
            phone=phone,
            location_type=location_type,
            latitude=lat,
            longitude=lng,
            hours_of_operation=hours.strip(),
        )


def scrape():
    log.info("Started")
    count = 0
    deduper = SgRecordDeduper(
        SgRecordID({SgRecord.Headers.LATITUDE, SgRecord.Headers.LONGITUDE})
    )
    with SgWriter(deduper) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
