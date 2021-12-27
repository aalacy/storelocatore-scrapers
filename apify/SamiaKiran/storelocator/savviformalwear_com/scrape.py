import html
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "savviformalwear_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://savviformalwear.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://savviformalwear.com/wp-admin/admin-ajax.php?action=store_search&lat=39.114053&lng=-94.6274636&max_results=500&search_radius=10000&filter=234&autoload=1"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            page_url = loc["permalink"]
            log.info(page_url)
            store_number = loc["id"]
            phone = loc["phone"]
            try:
                street_address = loc["address"] + " " + loc["address2"]
            except:
                street_address = loc["address"]
            hours_of_operation = loc["hours"]
            try:
                hours_of_operation = BeautifulSoup(hours_of_operation, "html.parser")
                hours_of_operation = hours_of_operation.get_text(
                    separator="|", strip=True
                ).replace("|", " ")
            except:
                hours_of_operation = MISSING
            location_type = loc["store"]
            location_type = html.unescape(location_type)
            location_name = location_type
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["zip"]
            country_code = loc["country"]
            latitude = loc["lat"]
            longitude = loc["lng"]

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=store_number,
                phone=phone.strip(),
                location_type=location_type,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
