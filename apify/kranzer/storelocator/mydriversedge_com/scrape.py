import html
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "mydriversedge_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://www.mydriversedge.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.mydriversedge.com/wp-admin/admin-ajax.php?action=store_search&lat=32.776664&lng=-96.796988&max_results=25&search_radius=50&autoload=1"
        loclist = session.get(url, headers=headers).json()
        for loc in loclist:
            location_name = html.unescape(loc["store"])
            page_url = loc["permalink"]
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            hours_of_operation = (
                soup.find("table", {"class": "hours-list"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            log.info(page_url)
            store_number = loc["id"]
            phone = loc["phone"]
            if not phone:
                phone = soup.find("a", {"class": "store-phone"}).text
            street_address = loc["address"]
            city = loc["city"]
            state = loc["state"]
            zip_postal = loc["zip"]
            country_code = "US"
            latitude = loc["lat"]
            longitude = loc["lng"]
            country_code = loc["country"]
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
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
