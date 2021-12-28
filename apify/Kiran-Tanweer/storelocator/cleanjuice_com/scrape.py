from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from bs4 import BeautifulSoup


session = SgRequests()
website = "cleanjuice_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "www.cleanjuice_com"
MISSING = SgRecord.MISSING


def fetch_data():
    search_url = "https://www.cleanjuice.com/wp-admin/admin-ajax.php?action=store_search&lat=35.227087&lng=-80.843127&max_results=50&search_radius=50&autoload=1"
    stores_req = session.get(search_url, headers=headers).json()
    for store in stores_req:
        street1 = store["address"]
        title = store["store"]
        storeid = store["id"]
        link = store["permalink"]
        street2 = store["address2"]
        city = store["city"]
        state = store["state"]
        pcode = store["zip"]
        country = store["country"]
        lat = store["lat"]
        lng = store["lng"]
        phone = store["phone"]
        hours = store["hours"]
        hours = BeautifulSoup(hours, "html.parser")
        hours = hours.text
        hours = hours.replace("day", "day ")
        hours = hours.replace("PM", "PM ")
        hours = hours.rstrip("Order Now")
        street = street1 + " " + street2
        if country == "United States":
            country = "US"

        pcode = pcode.replace("]", "").strip()

        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode,
            country_code=country,
            store_number=storeid,
            phone=phone,
            location_type=MISSING,
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
