from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


session = SgRequests()
website = "pokeworks_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://pokeworks.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        search_url = "https://pokeworks.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=1ac9e6a784&load_all=1&layout=1"
        stores_req = session.get(search_url, headers=headers).json()
        for store in stores_req:
            store_id = store["id"]
            title = store["title"]
            street = store["street"]
            city = store["city"]
            state = store["state"]
            pcode = store["postal_code"]
            lat = store["lat"]
            lng = store["lng"]
            phone = store["phone"]
            country = store["country"]
            hours = str(store["open_hours"])
            hours = hours.replace('"', "")
            hours = hours.replace("[", "")
            hours = hours.replace("]", "")
            hours = hours.replace("{", "")
            hours = hours.replace("}", "")
            hours = hours.replace(",", ", ")

            if hours == "mon:0, tue:0, wed:0, thu:0, fri:0, sat:0, sun:0":
                hours = MISSING

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://pokeworks.com/locations/",
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode,
                country_code=country,
                store_number=store_id,
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
        SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME})
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
