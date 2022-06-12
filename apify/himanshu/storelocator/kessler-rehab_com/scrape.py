import re
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "kessler-rehab_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.kessler-rehab.com"
MISSING = SgRecord.MISSING


def fetch_data():
    start_url = "https://www.kessler-rehab.com//sxa/search/results/?s={75078478-6727-4E71-8FC2-BED8FAD1B00B}&itemid={AF08CF64-F629-40A6-81AA-0B56D5A0185A}&sig=locations-cards&o=Title%2CAscending&p=20&v=%7BDD817789-9335-4441-B604-DC2901221E22%7D"
    stores = session.get(start_url, headers=headers).json()["Results"]
    for store in stores:
        soup = BeautifulSoup(store["Html"], "html.parser")
        page_url = DOMAIN + soup.find("a", string=re.compile("details"))["href"]
        log.info(page_url)
        location_name = soup.find("h3", {"class": "loc-result-card-name"}).text
        address = soup.findAll("a")[1].get_text(separator="|", strip=True).split("|")
        street_address = address[0]
        address = address[1].split(",")
        city = address[0]
        address = address[1].split()
        state = address[0]
        zip_postal = address[1]
        phone = soup.select_one("a[href*=tel]").text
        latitude, longitude = soup.find("img", {"class": "lazy"})["data-latlong"].split(
            "|"
        )
        hours_of_operation = (
            soup.find("div", {"class": "hours-table"})
            .get_text(separator="|", strip=True)
            .replace("|", " ")
        )
        country_code = "US"
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number=MISSING,
            phone=phone.strip(),
            location_type=MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation.strip(),
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
