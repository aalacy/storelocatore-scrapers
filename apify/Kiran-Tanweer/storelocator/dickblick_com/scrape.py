from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "dickblick_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.dickblick.com"
MISSING = SgRecord.MISSING


def fetch_data():
    url = "https://api.dickblick.com/blick/page-content/api/v4.0/store-page/list"
    store_list = session.get(url, headers=headers).json()
    for store in store_list:
        page_url = DOMAIN + store["storeUrl"]
        log.info(page_url)
        try:
            phone = store["store"]["phoneNumber"]
        except:
            phone = MISSING
        store_number = store["storeNumber"]
        location_name = store["storeName"]
        street_address = store["store"]["addressLine1"]
        city = store["store"]["city"]
        state = store["store"]["statePicker"]["stateAbbreviation"]
        zip_postal = store["store"]["zipCode"]
        latitude = store["store"]["coordinates"]["lat"]
        longitude = store["store"]["coordinates"]["lon"]
        r = session.get(page_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        hours_of_operation = (
            soup.find("div", {"class": "storelocation__top__hours"})
            .get_text(separator="|", strip=True)
            .replace("|", " ")
            .replace("Store Hours ", "")
        )
        country_code = "US"
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
