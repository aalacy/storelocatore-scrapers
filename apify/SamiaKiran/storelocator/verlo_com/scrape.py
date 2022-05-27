from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "verlo_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://verlo.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://verlo.com/wp-admin/admin-ajax.php?action=store_search&lat=43.0852217&lng=-88.0363086&max_results=100&search_radius=10000&autoload=1"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            location_name = loc["store"]
            store_number = loc["id"]
            phone = loc["phone"]
            page_url = loc["permalink"]
            log.info(page_url)
            try:
                street_address = loc["address"] + " " + loc["address2"]
            except:
                street_address = loc["address"]
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["zip"]
            country_code = loc["country"]
            latitude = loc["lat"]
            longitude = loc["lng"]
            hours_of_operation = loc["hours"]
            hours_of_operation = (
                BeautifulSoup(hours_of_operation, "html.parser")
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            if "PO BOX" in street_address:
                street_address = street_address.split(", PO BOX")[0]
            elif "Delafield" in street_address:
                street_address = street_address.split(", Delafield")[0]
            street_address = street_address.strip(",")

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
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
